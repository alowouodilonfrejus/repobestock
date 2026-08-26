from fastapi import APIRouter, Query, status

from app.api.deps import DbSession, PermDep, RolesDep
from app.crud import user as crud_user
from app.models.user import UserRole
from app.schemas.user import UserAdminCreate, UserList, UserRead, UserUpdate, UserValidation
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["users"])

AdminDep = RolesDep(UserRole.SUPERADMIN)
ReadDep = PermDep("users:read")
ValidateDep = PermDep("users:validate")


@router.get("", response_model=UserList)
async def read_users(
    db: DbSession,
    current_user: ReadDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
):
    items, total = await crud_user.list_users(db, skip=skip, limit=limit)
    return UserList(items=items, total=total, limit=limit, skip=skip)


@router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: int, db: DbSession, current_user: ReadDep):
    return await user_service.get_user_or_404(db, user_id)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserAdminCreate, db: DbSession, current_user: AdminDep):
    return await user_service.create_user(db, payload)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: DbSession,
    current_user: ValidateDep,
):
    return await user_service.update_user(db, user_id, payload, current_user)


@router.post("/{user_id}/valider", response_model=UserRead)
async def valider_user(
    user_id: int,
    db: DbSession,
    current_user: ValidateDep,
    payload: UserValidation | None = None,
):
    """Active un compte en attente de validation (admin et super admin)."""
    return await user_service.valider_user(db, user_id, payload, current_user)


@router.post("/{user_id}/rejeter", status_code=status.HTTP_204_NO_CONTENT)
async def rejeter_user(
    user_id: int,
    db: DbSession,
    current_user: ValidateDep,
):
    """Refuse une inscription : supprime le compte en attente et sa fiche employe."""
    await user_service.rejeter_user(db, user_id, current_user)
    return None


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: DbSession, current_user: AdminDep):
    await user_service.delete_user(db, user_id, current_user)
    return None