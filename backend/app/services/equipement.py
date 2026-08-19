from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import category as crud_category
from app.crud import emplacement as crud_emplacement
from app.crud import equipement as crud_equipement
from app.crud import historique as crud_historique
from app.crud import statut as crud_statut
from app.models.equipement import Equipement
from app.schemas.equipement import EquipementCreate, EquipementUpdate


async def _validate_fks(
    db: AsyncSession, categorie_id: int, statut_id: int, emplacement_id: int | None
) -> None:
    category = await crud_category.get_by_id(db, categorie_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Categorie {categorie_id} introuvable",
        )
    statut = await crud_statut.get_by_id(db, statut_id)
    if statut is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Statut {statut_id} introuvable",
        )
    if emplacement_id is not None:
        emplacement = await crud_emplacement.get_by_id(db, emplacement_id)
        if emplacement is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Emplacement {emplacement_id} introuvable",
            )


async def get_equipement_or_404(db: AsyncSession, equipement_id: int) -> Equipement:
    equipement = await crud_equipement.get_by_id(db, equipement_id)
    if equipement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipement introuvable",
        )
    return equipement


async def create_equipement(
    db: AsyncSession,
    payload: EquipementCreate,
    user_id: int,
    ip: str | None = None,
) -> Equipement:
    if await crud_equipement.get_by_reference(db, payload.reference):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette reference existe deja",
        )
    if payload.numero_serie and await crud_equipement.get_by_numero_serie(
        db, payload.numero_serie
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce numero de serie existe deja",
        )
    await _validate_fks(
        db, payload.categorie_id, payload.statut_id, payload.emplacement_id
    )

    equipement = await crud_equipement.create(db, payload, user_id=user_id)
    await crud_historique.create(
        db,
        equipement_id=equipement.id,
        action="creation",
        nouvelle_valeur=f"Creation de {payload.nom}",
        utilisateur_id=user_id,
        adresse_ip=ip,
    )
    return equipement


async def update_equipement(
    db: AsyncSession,
    equipement_id: int,
    payload: EquipementUpdate,
    user_id: int,
    ip: str | None = None,
) -> Equipement:
    equipement = await get_equipement_or_404(db, equipement_id)

    if (
        payload.reference
        and payload.reference != equipement.reference
        and await crud_equipement.get_by_reference(db, payload.reference)
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette reference existe deja",
        )
    if (
        payload.numero_serie
        and payload.numero_serie != equipement.numero_serie
        and await crud_equipement.get_by_numero_serie(db, payload.numero_serie)
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce numero de serie existe deja",
        )

    new_categorie_id = payload.categorie_id or equipement.categorie_id
    new_statut_id = payload.statut_id or equipement.statut_id
    new_emplacement_id = (
        payload.emplacement_id
        if payload.emplacement_id is not None
        else equipement.emplacement_id
    )
    await _validate_fks(db, new_categorie_id, new_statut_id, new_emplacement_id)

    ancienne = equipement.nom
    updated = await crud_equipement.update(
        db, equipement, payload, user_id=user_id
    )
    await crud_historique.create(
        db,
        equipement_id=updated.id,
        action="modification",
        ancienne_valeur=ancienne,
        nouvelle_valeur=updated.nom,
        utilisateur_id=user_id,
        adresse_ip=ip,
    )
    return updated


async def delete_equipement(
    db: AsyncSession, equipement_id: int, user_id: int, ip: str | None = None
) -> None:
    equipement = await get_equipement_or_404(db, equipement_id)
    nom = equipement.nom
    await crud_historique.create(
        db,
        equipement_id=equipement.id,
        action="suppression",
        ancienne_valeur=nom,
        utilisateur_id=user_id,
        adresse_ip=ip,
    )
    await crud_equipement.delete(db, equipement)