"""Logique metier de la maintenance des materiels.

Regles :
- un materiel ne peut avoir qu'UNE maintenance en cours
- au demarrage : statut passe a 'En maintenance', plus affectable
- a la cloture : retour possible au stock ('En stock')
- chaque operation produit mouvement + historique, en une transaction
"""

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import historique as crud_historique
from app.crud import maintenance as crud_maintenance
from app.crud import mouvements as crud_mouvements
from app.crud import statut as crud_statut
from app.models.maintenance import Maintenance, StatutMaintenance
from app.models.mouvement import Mouvement, TypeMouvement
from app.schemas.maintenance import MaintenanceCloture, MaintenanceCreate

STATUT_EN_MAINTENANCE = "En maintenance"
STATUT_EN_STOCK = "En stock"


async def get_or_404(db: AsyncSession, equipement_id: int):
    from app.services.equipement import get_equipement_or_404

    return await get_equipement_or_404(db, equipement_id)


async def demarrer_maintenance(
    db: AsyncSession,
    equipement_id: int,
    payload: MaintenanceCreate,
    user_id: int,
    ip: str | None = None,
) -> Maintenance:
    equipement = await get_or_404(db, equipement_id)

    if await crud_maintenance.get_en_cours(db, equipement_id) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une maintenance est deja en cours pour ce materiel",
        )

    try:
        id_maintenance = (
            await crud_statut.get_by_nom(db, STATUT_EN_MAINTENANCE)
        )
        if id_maintenance is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Statut 'En maintenance' manquant en base",
            )

        avant = equipement.quantite_disponible
        maintenance = Maintenance(
            equipement_id=equipement_id,
            user_id=user_id,
            date_debut=payload.date_debut or date.today(),
            motif=payload.motif,
            description=payload.description,
            cout=payload.cout,
            technicien=payload.technicien,
            statut=StatutMaintenance.EN_COURS,
            commentaire=payload.commentaire,
        )
        db.add(maintenance)
        await db.flush()

        equipement.statut_id = id_maintenance.id
        # Ne pas toucher a quantite_disponible : le statut 'En maintenance'
        # suffit a bloquer les affectations (STATUTS_BLOQUES). Ainsi on
        # preserve le nombre exact d'exemplaires affectes avant maintenance.

        await crud_mouvements.create(
            db,
            Mouvement(
                equipement_id=equipement_id,
                user_id=user_id,
                type=TypeMouvement.MAINTENANCE,
                quantite=equipement.quantite,
                quantite_avant=avant,
                quantite_apres=0,
                ref_type="maintenance",
                ref_id=maintenance.id,
                commentaire=payload.motif,
            ),
        )
        await crud_historique.create_no_commit(
            db,
            equipement_id=equipement_id,
            action="maintenance",
            nouvelle_valeur=f"Entree en maintenance ({payload.motif or 'sans motif'})",
            utilisateur_id=user_id,
            adresse_ip=ip,
        )
        await db.commit()
    except HTTPException:
        await db.rollback()
        raise
    except Exception as exc:
        await db.rollback()
        import logging

        logging.getLogger(__name__).exception("Echec demarrage maintenance")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Echec du demarrage maintenance",
        ) from exc

    # Recharger avec les relations (equipement) pour la serialisation.
    return await crud_maintenance.get_by_id(db, maintenance.id)


async def cloturer_maintenance(
    db: AsyncSession,
    maintenance_id: int,
    payload: MaintenanceCloture,
    user_id: int,
    ip: str | None = None,
) -> Maintenance:
    maintenance = await crud_maintenance.get_by_id(db, maintenance_id)
    if maintenance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance introuvable",
        )
    if maintenance.statut == StatutMaintenance.TERMINEE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maintenance deja terminee",
        )

    try:
        id_en_stock = await crud_statut.get_by_nom(db, STATUT_EN_STOCK)
        if id_en_stock is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Statut 'En stock' manquant en base",
            )

        equipement = maintenance.equipement
        maintenance.date_fin = payload.date_fin or date.today()
        maintenance.statut = StatutMaintenance.TERMINEE
        if payload.commentaire:
            maintenance.commentaire = (
                f"{maintenance.commentaire}\n[cloture] {payload.commentaire}".strip()
            )

        avant = equipement.quantite_disponible
        equipement.statut_id = id_en_stock.id
        # quantite_disponible reste inchangee (preservee depuis le demarrage)

        await crud_mouvements.create(
            db,
            Mouvement(
                equipement_id=equipement.id,
                user_id=user_id,
                type=TypeMouvement.RETOUR,
                quantite=equipement.quantite,
                quantite_avant=avant,
                quantite_apres=equipement.quantite_disponible,
                ref_type="maintenance",
                ref_id=maintenance.id,
                commentaire="Retour de maintenance",
            ),
        )
        await crud_historique.create_no_commit(
            db,
            equipement_id=equipement.id,
            action="maintenance",
            ancienne_valeur="En maintenance",
            nouvelle_valeur=f"Maintenance terminee le {maintenance.date_fin}",
            utilisateur_id=user_id,
            adresse_ip=ip,
        )
        await db.commit()
    except HTTPException:
        await db.rollback()
        raise
    except Exception as exc:
        await db.rollback()
        import logging

        logging.getLogger(__name__).exception("Echec cloture maintenance")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Echec de la cloture",
        ) from exc

    return await crud_maintenance.get_by_id(db, maintenance_id)
