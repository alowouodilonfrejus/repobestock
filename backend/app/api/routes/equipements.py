from fastapi import APIRouter, Query, Request, status

from app.api.deps import ActiveUser, DbSession, get_client_ip
from app.crud import equipement as crud_equipement
from app.crud import historique as crud_historique
from app.schemas.equipement import (
    EquipementCreate,
    EquipementList,
    EquipementRead,
    EquipementStats,
    EquipementUpdate,
)
from app.schemas.historique import HistoriqueRead
from app.services import equipement as equipement_service

router = APIRouter(prefix="/equipements", tags=["equipements"])


@router.get("", response_model=EquipementList)
async def read_equipements(
    db: DbSession,
    current_user: ActiveUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    categorie_id: int | None = Query(None),
):
    items, total = await crud_equipement.list_equipements(
        db, skip=skip, limit=limit, categorie_id=categorie_id
    )
    return EquipementList(items=items, total=total, limit=limit, skip=skip)


@router.get("/stats", response_model=EquipementStats)
async def read_equipement_stats(
    db: DbSession,
    current_user: ActiveUser,
    maintenance_statut_id: int | None = Query(None),
):
    from app.crud import statut as crud_statut

    total = await crud_equipement.count_total(db)
    maintenance = 0
    if maintenance_statut_id is not None:
        maintenance = await crud_equipement.count_by_statut(db, maintenance_statut_id)
    else:
        statut = await crud_statut.get_by_nom(db, "En maintenance")
        if statut is not None:
            maintenance = await crud_equipement.count_by_statut(db, statut.id)
    recent = await crud_equipement.list_recent(db, limit=8)
    return EquipementStats(total=total, maintenance=maintenance, recent=recent)


@router.post(
    "", response_model=EquipementRead, status_code=status.HTTP_201_CREATED
)
async def create_equipement(
    payload: EquipementCreate,
    request: Request,
    db: DbSession,
    current_user: ActiveUser,
):
    return await equipement_service.create_equipement(
        db,
        payload,
        user_id=current_user.id,
        ip=await get_client_ip(request),
    )


@router.get("/{equipement_id}", response_model=EquipementRead)
async def read_equipement(
    equipement_id: int, db: DbSession, current_user: ActiveUser
):
    return await equipement_service.get_equipement_or_404(db, equipement_id)


@router.get("/{equipement_id}/historique", response_model=list[HistoriqueRead])
async def read_equipement_historique(
    equipement_id: int, db: DbSession, current_user: ActiveUser
):
    return await crud_historique.list_for_equipement(db, equipement_id)


@router.put("/{equipement_id}", response_model=EquipementRead)
async def update_equipement(
    equipement_id: int,
    payload: EquipementUpdate,
    request: Request,
    db: DbSession,
    current_user: ActiveUser,
):
    return await equipement_service.update_equipement(
        db,
        equipement_id,
        payload,
        user_id=current_user.id,
        ip=await get_client_ip(request),
    )


@router.delete("/{equipement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipement(
    equipement_id: int,
    request: Request,
    db: DbSession,
    current_user: ActiveUser,
):
    await equipement_service.delete_equipement(
        db,
        equipement_id,
        user_id=current_user.id,
        ip=await get_client_ip(request),
    )
    return None