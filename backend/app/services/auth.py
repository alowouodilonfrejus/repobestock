from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, generate_refresh_token
from app.crud import refresh_token as crud_refresh
from app.crud import user as crud_user
from app.models.user import UserRole
from app.schemas.token import LoginRequest, RefreshRequest, Token
from app.schemas.user import UserCreate


async def register(db: AsyncSession, payload: UserCreate):
    existing = await crud_user.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet email est deja utilise",
        )
    requested_role = payload.role or UserRole.MANAGER
    if requested_role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role non autorise a l'inscription",
        )
    return await crud_user.create(
        db, payload, role=requested_role, is_active=False
    )


async def login(db: AsyncSession, payload: LoginRequest) -> Token:
    user = await crud_user.authenticate(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte en attente de validation par le super admin",
        )
    refresh_token = generate_refresh_token()
    await crud_refresh.create(db, user.id, refresh_token)
    return Token(
        access_token=create_access_token(str(user.id)),
        refresh_token=refresh_token,
    )


async def refresh(db: AsyncSession, payload: RefreshRequest) -> Token:
    """Echange un refresh token valide contre un nouveau couple access + refresh."""
    refresh = await crud_refresh.get_by_token(db, payload.refresh_token)
    if refresh is None or refresh.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide",
        )
    if refresh.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expire",
        )

    user = await crud_user.get_by_id(db, refresh.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur invalide ou desactive",
        )

    await crud_refresh.revoke(db, refresh)
    new_refresh_token = generate_refresh_token()
    await crud_refresh.create(db, user.id, new_refresh_token)
    return Token(
        access_token=create_access_token(str(user.id)),
        refresh_token=new_refresh_token,
    )


async def logout(db: AsyncSession, payload: RefreshRequest) -> None:
    refresh = await crud_refresh.get_by_token(db, payload.refresh_token)
    if refresh is not None:
        await crud_refresh.revoke(db, refresh)