from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user as crud_user
from app.models.user import User, UserRole
from app.schemas.user import UserAdminCreate, UserUpdate


async def _count_active_superadmins(db: AsyncSession) -> int:
    users, _ = await crud_user.list_users(db, limit=1000)
    return sum(1 for u in users if u.role == UserRole.SUPERADMIN and u.is_active)


async def get_user_or_404(db: AsyncSession, user_id: int) -> User:
    user = await crud_user.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable"
        )
    return user


async def create_user(db: AsyncSession, payload: UserAdminCreate) -> User:
    if await crud_user.get_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet email est deja utilise",
        )
    return await crud_user.create(db, payload, role=payload.role)


async def update_user(
    db: AsyncSession, user_id: int, payload: UserUpdate, current_user: User
) -> User:
    user = await get_user_or_404(db, user_id)
    data = payload.model_dump(exclude_unset=True)

    if user.id == current_user.id:
        if data.get("role") is not None and data["role"] != user.role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous ne pouvez pas changer votre propre role",
            )
        if data.get("is_active") is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous ne pouvez pas desactiver votre propre compte",
            )

    is_last_superadmin = (
        user.role == UserRole.SUPERADMIN
        and user.is_active
        and await _count_active_superadmins(db) == 1
    )
    if is_last_superadmin:
        if data.get("is_active") is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de desactiver le dernier super admin",
            )
        if data.get("role") is not None and data["role"] != UserRole.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de retirer le role du dernier super admin",
            )

    return await crud_user.update(db, user, data)


async def delete_user(db: AsyncSession, user_id: int, current_user: User) -> None:
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas supprimer votre propre compte",
        )

    user = await get_user_or_404(db, user_id)

    if (
        user.role == UserRole.SUPERADMIN
        and user.is_active
        and await _count_active_superadmins(db) == 1
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer le dernier super admin",
        )

    await crud_user.delete(db, user)