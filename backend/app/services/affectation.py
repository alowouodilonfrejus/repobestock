"""Logique metier des affectations de materiels aux employes.

Regles verrouillees cote serveur :
- quantite_disponible = quantite - somme(quantites actuellement affectees)
- refus si affectation > disponible, quantite <= 0, materiel en maintenance
  ou hors service
- multi-affectation = UNE SEULE transaction (rollback total si echec)
- chaque operation produit un mouvement + une entree historique
- l'historique n'est jamais supprime ni modifie
"""

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import affectation as crud_affectation
from app.crud import employe as crud_employe
from app.crud import equipement as crud_equipement
from app.crud import historique as crud_historique
from app.crud import mouvements as crud_mouvements
from app.crud import statut as crud_statut
from app.models.affectation import Affectation, AffectationItem, StatutAffectation
from app.models.equipement import Equipement, EtatMateriel
from app.models.mouvement import Mouvement, TypeMouvement
from app.schemas.affectation import AffectationCreate, RetourCreate

# Statuts interdisant toute nouvelle affectation.
STATUTS_BLOQUES = ("En maintenance", "Hors service", "Perdu")

# Statuts cibles apres operations.
STATUT_AFFECTE = "Affecte"
STATUT_EN_STOCK = "En stock"
STATUT_ENDOMMAGE = "Endommage"


async def _get_statut_id(db: AsyncSession, nom: str) -> int:
    statut = await crud_statut.get_by_nom(db, nom)
    if statut is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Statut de reference manquant en base : {nom}",
        )
    return statut.id


def _verifier_quantite(equipement: Equipement, quantite: int) -> None:
    if quantite <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La quantite doit etre strictement positive",
        )
    if quantite > equipement.quantite_disponible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"{equipement.reference} : demande {quantite}, "
                f"disponible {equipement.quantite_disponible}"
            ),
        )


async def _charger_equipements_verrouilles(
    db: AsyncSession, equipement_ids: list[int]
) -> dict[int, Equipement]:
    """Charge les equipements avec verrou de ligne (anti-course concurrente)."""
    result = await db.execute(
        select(Equipement)
        .options(selectinload(Equipement.statut))
        .where(Equipement.id.in_(equipement_ids))
        .with_for_update()
    )
    equipements = {eq.id: eq for eq in result.scalars().all()}
    for eid in equipement_ids:
        if eid not in equipements:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Equipement {eid} introuvable",
            )
    return equipements


async def create_affectation(
    db: AsyncSession,
    payload: AffectationCreate,
    user_id: int,
    ip: str | None = None,
) -> Affectation:
    """Affecte un ou plusieurs materiels a un employe en une seule transaction."""
    employe = await crud_employe.get_by_id(db, payload.employe_id)
    if employe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employe introuvable"
        )
    if not employe.actif:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible d'affecter du materiel a un employe inactif",
        )

    date_affectation = payload.date_affectation or date.today()
    if payload.date_retour_prevue and payload.date_retour_prevue < date_affectation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La date de retour prevue ne peut pas preceder la date d'affectation",
        )

    # Doublons dans la meme demande : fusionner pour garder des totaux coherents.
    demandes: dict[int, tuple[int, EtatMateriel]] = {}
    for item in payload.items:
        qte, etat = demandes.get(item.equipement_id, (0, item.etat_affectation))
        demandes[item.equipement_id] = (
            qte + item.quantite,
            etat or item.etat_affectation,
        )

    try:
        equipements = await _charger_equipements_verrouilles(
            db, list(demandes.keys())
        )
        id_affecte = await _get_statut_id(db, STATUT_AFFECTE)

        # --- Phase validation : tout est verifie avant toute ecriture ---
        for eid, (quantite, _etat) in demandes.items():
            equipement = equipements[eid]
            nom_statut = equipement.statut.nom if equipement.statut else None
            if nom_statut in STATUTS_BLOQUES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"{equipement.reference} : statut '{nom_statut}' "
                        f"interdit pour une affectation"
                    ),
                )
            _verifier_quantite(equipement, quantite)

        # --- Phase ecriture : un seul commit a la fin ---
        affectation = Affectation(
            employe_id=payload.employe_id,
            cree_par=user_id,
            date_affectation=date_affectation,
            date_retour_prevue=payload.date_retour_prevue,
            motif=payload.motif,
            commentaire=payload.commentaire,
            statut=StatutAffectation.ACTIVE,
        )
        db.add(affectation)
        await db.flush()

        for eid, (quantite, etat) in demandes.items():
            equipement = equipements[eid]
            avant = equipement.quantite_disponible

            item = AffectationItem(
                affectation_id=affectation.id,
                equipement_id=eid,
                quantite=quantite,
                etat_affectation=etat.value,
            )
            db.add(item)

            equipement.quantite_disponible -= quantite
            if equipement.quantite_disponible == 0:
                equipement.statut_id = id_affecte

            db.add(
                Mouvement(
                    equipement_id=eid,
                    employe_id=employe.id,
                    user_id=user_id,
                    type=TypeMouvement.AFFECTATION,
                    quantite=quantite,
                    quantite_avant=avant,
                    quantite_apres=equipement.quantite_disponible,
                    etat=etat.value,
                    ref_type="affectation",
                    ref_id=affectation.id,
                )
            )
            await crud_historique.create_no_commit(
                db,
                equipement_id=eid,
                action="affectation",
                nouvelle_valeur=f"Affecte x{quantite} a {employe.nom_complet}",
                utilisateur_id=user_id,
                adresse_ip=ip,
            )

        await db.commit()
    except HTTPException:
        await db.rollback()
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Echec de l'affectation, transaction annulee : {exc}",
        ) from exc

    await db.refresh(affectation)
    return await crud_affectation.get_by_id(db, affectation.id)


async def process_retour(
    db: AsyncSession,
    affectation_id: int,
    payload: RetourCreate,
    user_id: int,
    ip: str | None = None,
) -> Affectation:
    """Enregistre le retour (total ou partiel) de materiels affectes."""
    affectation = await crud_affectation.get_by_id(db, affectation_id)
    if affectation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Affectation introuvable"
        )
    if affectation.statut not in (StatutAffectation.ACTIVE, StatutAffectation.PARTIELLE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Affectation deja cloturee (statut : {affectation.statut.value})",
        )

    date_retour = payload.date_retour or date.today()

    items_par_id = {item.id: item for item in affectation.items}
    for retour in payload.items:
        if retour.affectation_item_id not in items_par_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Ligne {retour.affectation_item_id} n'appartient pas "
                    f"a cette affectation"
                ),
            )

    try:
        equipements = await _charger_equipements_verrouilles(
            db,
            [
                items_par_id[r.affectation_item_id].equipement_id
                for r in payload.items
            ],
        )
        id_en_stock = await _get_statut_id(db, STATUT_EN_STOCK)
        id_endommage = await _get_statut_id(db, STATUT_ENDOMMAGE)

        # --- Validation des quantites retournables ---
        for retour in payload.items:
            item = items_par_id[retour.affectation_item_id]
            restant = item.quantite - item.quantite_retournee
            if retour.quantite_retournee > restant:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Ligne {item.id} : retour {retour.quantite_retournee} "
                        f"> reste a retourner {restant}"
                    ),
                )

        # --- Ecritures ---
        for retour in payload.items:
            item = items_par_id[retour.affectation_item_id]
            equipement = equipements[item.equipement_id]
            avant = equipement.quantite_disponible

            item.quantite_retournee += retour.quantite_retournee
            item.etat_retour = retour.etat_retour.value
            item.date_retour = date_retour
            item.accessoires_retournes = retour.accessoires_retournes
            item.probleme_constate = retour.probleme_constate
            if retour.commentaire:
                item.commentaire = retour.commentaire

            equipement.quantite_disponible += retour.quantite_retournee
            if retour.etat_retour == EtatMateriel.ENDOMMAGE:
                equipement.statut_id = id_endommage
            elif equipement.quantite_disponible >= equipement.quantite:
                equipement.statut_id = id_en_stock

            db.add(
                Mouvement(
                    equipement_id=item.equipement_id,
                    employe_id=affectation.employe_id,
                    user_id=user_id,
                    type=TypeMouvement.RETOUR,
                    quantite=retour.quantite_retournee,
                    quantite_avant=avant,
                    quantite_apres=equipement.quantite_disponible,
                    etat=retour.etat_retour.value,
                    ref_type="affectation",
                    ref_id=affectation.id,
                    commentaire=retour.probleme_constate or retour.commentaire,
                )
            )
            await crud_historique.create_no_commit(
                db,
                equipement_id=item.equipement_id,
                action="retour",
                ancienne_valeur=f"Affecte a {affectation.employe.nom_complet}",
                nouvelle_valeur=(
                    f"Retour x{retour.quantite_retournee} "
                    f"(etat : {retour.etat_retour.value})"
                ),
                utilisateur_id=user_id,
                adresse_ip=ip,
            )

        tout_rendu = all(
            it.quantite_retournee >= it.quantite for it in affectation.items
        )
        affectation.statut = (
            StatutAffectation.RETOURNEE
            if tout_rendu
            else StatutAffectation.PARTIELLE
        )
        if payload.commentaire:
            affectation.commentaire = (
                f"{affectation.commentaire}\n[retour] {payload.commentaire}".strip()
            )

        await db.commit()
    except HTTPException:
        await db.rollback()
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Echec du retour, transaction annulee : {exc}",
        ) from exc

    return await crud_affectation.get_by_id(db, affectation_id)


async def list_materiels_attribues(
    db: AsyncSession, employe_id: int
) -> list[AffectationItem]:
    """Materiels actuellement sous la responsabilite d'un employe.

    L'ancien employe reste visible dans l'historique/mouvements :
    cette vue ne montre que ce qui est encore detenu.
    """
    result = await db.execute(
        select(AffectationItem)
        .join(Affectation, AffectationItem.affectation_id == Affectation.id)
        .options(
            selectinload(AffectationItem.affectation),
            selectinload(AffectationItem.equipement),
        )
        .where(
            Affectation.employe_id == employe_id,
            Affectation.statut.in_(
                [StatutAffectation.ACTIVE, StatutAffectation.PARTIELLE]
            ),
        )
        .order_by(Affectation.date_affectation.desc())
    )
    return list(result.scalars().unique().all())
