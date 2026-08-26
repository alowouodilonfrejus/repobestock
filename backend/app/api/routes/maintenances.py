from fastapi import APIRouter, Query, Request, status

from app.api.deps import ActiveUser, DbSession, PermDep, get_client_ip
from app.crud import maintenance as crud_maintenance
from app.models.user import UserRole
from app.schemas.maintenance import (
    MaintenanceCloture,
    MaintenanceCreate,
    MaintenanceList,
    MaintenanceRead,
)
from app.services import maintenance as maintenance_service

router = APIRouter(prefix="/maintenances", tags=["maintenances"])

ReadDep = PermDep("maintenances:read")
WriteDep = PermDep("maintenances:write")


@router.post(
    "/equipement/{equipement_id}",
    response_model=MaintenanceRead,
    status_code=status.HTTP_201_CREATED,
)
async def demarrer_maintenance(
    equipement_id: int,
    payload: MaintenanceCreate,
    request: Request,
    db: DbSession,
    current_user: WriteDep,
):
    """Declare un materiel en maintenance : plus affectable pendant l'operation."""
    return await maintenance_service.demarrer_maintenance(
        db,
        equipement_id,
        payload,
        user_id=current_user.id,
        ip=await get_client_ip(request),
    )


@router.get("/moi", response_model=list[MaintenanceRead])
async def read_mes_incidents(db: DbSession, current_user: ActiveUser):
    """Incidents (maintenances) des materiels affectes au compte connecte."""
    items, _total = await crud_maintenance.list_for_user(db, current_user.id)
    return items


@router.get("", response_model=MaintenanceList)
async def read_maintenances(
    db: DbSession,
    current_user: ReadDep,
    equipement_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    items, total = await crud_maintenance.list_maintenances(
        db, skip=skip, limit=limit, equipement_id=equipement_id
    )
    return MaintenanceList(items=items, total=total)


@router.get("/equipement/{equipement_id}", response_model=list[MaintenanceRead])
async def read_historique_maintenance(
    equipement_id: int, db: DbSession, current_user: ReadDep
):
    items, _total = await crud_maintenance.list_maintenances(
        db, equipement_id=equipement_id
    )
    return items


@router.post("/{maintenance_id}/cloture", response_model=MaintenanceRead)
async def cloturer_maintenance(
    maintenance_id: int,
    payload: MaintenanceCloture,
    request: Request,
    db: DbSession,
    current_user: WriteDep,
):
    """Termine la maintenance : le materiel redevient disponible."""
    return await maintenance_service.cloturer_maintenance(
        db,
        maintenance_id,
        payload,
        user_id=current_user.id,
        ip=await get_client_ip(request),
    )
