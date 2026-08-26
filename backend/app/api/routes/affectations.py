from fastapi import APIRouter, Query, Request, status

from app.api.deps import ActiveUser, DbSession, PermDep, get_client_ip
from app.crud import affectation as crud_affectation
from app.crud import employe as crud_employe
from app.models.affectation import StatutAffectation
from app.models.user import UserRole
from app.schemas.affectation import AffectationCreate, AffectationList, AffectationRead, RetourCreate
from app.services import affectation as affectation_service

router = APIRouter(prefix="/affectations", tags=["affectations"])

ReadDep = PermDep("affectations:read")
WriteDep = PermDep("affectations:write")


@router.post(
    "", response_model=AffectationRead, status_code=status.HTTP_201_CREATED
)
async def create_affectation(
    payload: AffectationCreate,
    request: Request,
    db: DbSession,
    current_user: WriteDep,
):
    """Affecte un ou plusieurs materiels a un employe (transaction unique)."""
    return await affectation_service.create_affectation(
        db,
        payload,
        user_id=current_user.id,
        ip=await get_client_ip(request),
    )


@router.get("", response_model=AffectationList)
async def read_affectations(
    db: DbSession,
    current_user: ReadDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    employe_id: int | None = Query(None),
    statut: StatutAffectation | None = Query(None),
):
    items, total = await crud_affectation.list_affectations(
        db, skip=skip, limit=limit, employe_id=employe_id, statut=statut
    )
    return AffectationList(items=items, total=total, limit=limit, skip=skip)


@router.get("/moi", response_model=list[AffectationRead])
async def read_mes_affectations(db: DbSession, current_user: ActiveUser):
    """Affectations du compte connecte (consultation employe)."""
    employe = await crud_employe.get_by_user_id(db, current_user.id)
    if employe is None:
        return []
    items, _total = await crud_affectation.list_affectations(
        db, limit=100, employe_id=employe.id
    )
    return items


@router.get("/{affectation_id}", response_model=AffectationRead)
async def read_affectation(
    affectation_id: int, db: DbSession, current_user: ReadDep
):
    affectation = await crud_affectation.get_by_id(db, affectation_id)
    if affectation is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Affectation introuvable")
    return affectation


@router.post("/{affectation_id}/retour", response_model=AffectationRead)
async def retour_materiel(
    affectation_id: int,
    payload: RetourCreate,
    request: Request,
    db: DbSession,
    current_user: WriteDep,
):
    """Enregistre le retour (total ou partiel) de materiels."""
    return await affectation_service.process_retour(
        db,
        affectation_id,
        payload,
        user_id=current_user.id,
        ip=await get_client_ip(request),
    )
