from fastapi import HTTPException, status
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import employe as crud_employe
from app.crud import user as crud_user
from app.models.affectation import Affectation
from app.models.equipement import Equipement
from app.models.historique import Historique
from app.models.mouvement import Mouvement
from app.models.user import User, UserRole
from app.schemas.user import UserAdminCreate, UserUpdate, UserValidation


async def _count_active_superadmins(db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count()).select_from(User).where(User.role == UserRole.SUPERADMIN, User.is_active.is_(True))
    )
    return result.scalar_one() or 0


_ROLE_RANKS = {
    UserRole.EMPLOYE: 0,
    UserRole.MANAGER: 1,
    UserRole.ADMIN: 2,
    UserRole.SUPERADMIN: 3,
}


def _verifier_role_attribuable(role: UserRole, current_user: User) -> None:
    """Un utilisateur ne peut attribuer que des roles strictement inferieurs au sien."""
    if current_user.role == UserRole.SUPERADMIN:
        return
    if _ROLE_RANKS[role] >= _ROLE_RANKS[current_user.role]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas attribuer un role egal ou superieur au votre",
        )


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

    nouvelle_role = data.get("role")
    if nouvelle_role is not None:
        _verifier_role_attribuable(nouvelle_role, current_user)

    if current_user.role != UserRole.SUPERADMIN and user.id != current_user.id:
        if _ROLE_RANKS[user.role] >= _ROLE_RANKS[current_user.role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez modifier que les comptes de rang inferieur au votre",
            )

    if user.id == current_user.id and current_user.role != UserRole.SUPERADMIN:
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


async def valider_user(
    db: AsyncSession, user_id: int, payload: UserValidation | None, current_user: User
) -> User:
    """Active un compte en attente et lui attribue son role final."""
    user = await get_user_or_404(db, user_id)
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte est deja actif",
        )
    data: dict = {"is_active": True}
    if payload is not None and payload.role is not None:
        _verifier_role_attribuable(payload.role, current_user)
        if user.id == current_user.id and current_user.role != UserRole.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous ne pouvez pas valider votre propre compte",
            )
        data["role"] = payload.role
    return await crud_user.update(db, user, data)


async def rejeter_user(db: AsyncSession, user_id: int, current_user: User) -> None:
    """Supprime un compte en attente de validation et sa fiche employe liee."""
    if user_id == current_user.id and current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas rejeter votre propre compte",
        )
    user = await get_user_or_404(db, user_id)
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seul un compte en attente de validation peut etre rejete",
        )
    employe = await crud_employe.get_by_user_id(db, user.id)
    if employe is not None:
        await crud_employe.delete(db, employe)
    await crud_user.delete(db, user)


async def delete_user(db: AsyncSession, user_id: int, current_user: User) -> None:
    if user_id == current_user.id and current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas supprimer votre propre compte",
        )

    user = await get_user_or_404(db, user_id)

    if current_user.role != UserRole.SUPERADMIN and _ROLE_RANKS[user.role] >= _ROLE_RANKS[current_user.role]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas supprimer un compte de rang supérieur ou égal au vôtre",
        )

    if (
        user.role == UserRole.SUPERADMIN
        and user.is_active
        and await _count_active_superadmins(db) == 1
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer le dernier super admin",
        )

    # Traces d'audit : anonymisation des colonnes nullables,
    # reassignment des affectations (cree_par est NOT NULL).
    await db.execute(
        update(Historique).where(Historique.utilisateur_id == user.id).values(utilisateur_id=None)
    )
    await db.execute(
        update(Mouvement).where(Mouvement.user_id == user.id).values(user_id=None)
    )
    await db.execute(
        update(Equipement).where(Equipement.created_by == user.id).values(created_by=None)
    )
    await db.execute(
        update(Equipement).where(Equipement.updated_by == user.id).values(updated_by=None)
    )
    await db.execute(
        update(Affectation).where(Affectation.cree_par == user.id).values(cree_par=current_user.id)
    )

    # Fiche collaborateur liee : supprimee si sans affectation, sinon detachee.
    employe = await crud_employe.get_by_user_id(db, user.id)
    if employe is not None:
        nb_affectations = await db.scalar(
            select(func.count()).select_from(Affectation).where(Affectation.employe_id == employe.id)
        )
        if nb_affectations:
            employe.user_id = None
            db.add(employe)
            await db.flush()
        else:
            await crud_employe.delete(db, employe)

    from app.models.refresh_token import RefreshToken

    await db.execute(delete(RefreshToken).where(RefreshToken.user_id == user.id))
    await crud_user.delete(db, user)