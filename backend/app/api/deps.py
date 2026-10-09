from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.cookies import ACCESS_COOKIE
from app.core.security import decode_access_token
from app.crud import user as crud_user
from app.db.session import get_db
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/json",
    # auto_error=False : a l'absence d'en-tete Authorization on retombe
    # sur le cookie httpOnly (navigation du frontend)
    auto_error=False,
)

DbSession = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str | None, Depends(oauth2_scheme)]


async def get_current_user(
    db: DbSession, token: TokenDep, request: Request
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expire",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        token = request.cookies.get(ACCESS_COOKIE)
    if not token:
        raise credentials_error

    payload = decode_access_token(token)
    if payload is None or payload.get("sub") is None:
        raise credentials_error

    try:
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        raise credentials_error

    user = await crud_user.get_by_id(db, user_id)
    if user is None:
        raise credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_user(current_user: CurrentUser) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte en attente de validation par le super admin",
        )
    return current_user


ActiveUser = Annotated[User, Depends(get_current_active_user)]


def require_roles(*roles: UserRole):
    async def _checker(current_user: ActiveUser) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privileges insuffisants",
            )
        return current_user

    return _checker


def RolesDep(*roles: UserRole):
    return Annotated[User, Depends(require_roles(*roles))]


def require_permission(permission: str):
    """Role Guard base sur la matrice centralisee app/core/permissions.py."""

    from app.core.permissions import is_superadmin, role_has
    import logging

    async def _checker(current_user: ActiveUser) -> User:
        if not role_has(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privileges insuffisants",
            )
        # Audit : tracer tout acces SUPERADMIN via wildcard
        if is_superadmin(current_user.role) and permission != "*":
            logging.getLogger("bestock.rbac").info(
                "SUPERADMIN wildcard: user=%s (%s) permission=%s",
                current_user.id,
                current_user.email,
                permission,
            )
        return current_user

    return _checker


def PermDep(permission: str):
    return Annotated[User, Depends(require_permission(permission))]


async def get_client_ip(request: Request) -> str | None:
    # Derriere reverse-proxy (Nginx/Traefik) l'IP reelle est dans
    # X-Forwarded-For — uniquement si TRUST_PROXY est active
    # (meme regle que le rate limiting, cf. app/middleware/rate_limit.py)
    from app.middleware.rate_limit import client_ip

    ip = client_ip(request)
    return None if ip in {"?", ""} else ip
