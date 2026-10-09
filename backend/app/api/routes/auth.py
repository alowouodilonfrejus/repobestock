from fastapi import APIRouter, HTTPException, Request, Response, status

from app.api.deps import ActiveUser, DbSession
from app.core.cookies import (
    ACCESS_COOKIE,
    REFRESH_COOKIE,
    clear_auth_cookies,
    set_auth_cookies,
)
from app.core.permissions import role_permissions
from app.schemas.token import LoginRequest, RefreshRequest, Token
from app.schemas.user import UserMeRead
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _extract_refresh_token(
    request: Request, payload: RefreshRequest | None
) -> str:
    """Refresh token : corps JSON (clients API) puis cookie httpOnly (frontend)."""
    if payload and payload.refresh_token:
        return payload.refresh_token
    token = request.cookies.get(REFRESH_COOKIE)
    if token:
        return token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token manquant",
    )


@router.post("/login/json", response_model=Token)
async def login_json(
    payload: LoginRequest, db: DbSession, request: Request, response: Response
):
    """Login en JSON — utilise par le frontend Nuxt (email + mot de passe).

    Les tokens sont aussi fixes en cookies httpOnly (navigation du frontend) ;
    le corps JSON reste disponible pour les clients API et les tests.
    """
    token = await auth_service.login(db, payload)
    set_auth_cookies(response, request, token)
    return token


@router.post("/refresh", response_model=Token)
async def refresh(
    db: DbSession,
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
):
    """Echange un refresh token valide contre un nouveau couple access + refresh.

    Source du token : corps JSON ou cookie httpOnly bestock_refresh.
    """
    token_str = _extract_refresh_token(request, payload)
    token = await auth_service.refresh(db, RefreshRequest(refresh_token=token_str))
    set_auth_cookies(response, request, token)
    return token


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    db: DbSession,
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
):
    token_str = None
    if payload and payload.refresh_token:
        token_str = payload.refresh_token
    else:
        token_str = request.cookies.get(REFRESH_COOKIE)
    if token_str:
        await auth_service.logout(db, RefreshRequest(refresh_token=token_str))
    # Cookies effaces meme si le token est deja invalide
    clear_auth_cookies(response, request)
    return None


@router.get("/me", response_model=UserMeRead)
async def read_me(current_user: ActiveUser):
    perms = sorted(role_permissions(current_user.role))
    # UserMeRead herite de UserRead : on hydrate depuis l'ORM + permissions
    data = UserMeRead.model_validate(current_user)
    data.permissions = perms
    return data


@router.get("/permissions", response_model=list[str])
async def read_my_permissions(current_user: ActiveUser):
    """Liste brute des permissions du compte connecte (utile pour debug front)."""
    return sorted(role_permissions(current_user.role))
