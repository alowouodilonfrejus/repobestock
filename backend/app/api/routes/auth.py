from fastapi import APIRouter, status

from app.api.deps import ActiveUser, DbSession
from app.core.permissions import role_permissions
from app.schemas.token import LoginRequest, RefreshRequest, Token
from app.schemas.user import UserMeRead, UserRead
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login/json", response_model=Token)
async def login_json(payload: LoginRequest, db: DbSession):
    """Login en JSON — utilise par le frontend Nuxt (email + mot de passe)."""
    return await auth_service.login(db, payload)


@router.post("/refresh", response_model=Token)
async def refresh(payload: RefreshRequest, db: DbSession):
    """Echange un refresh token valide contre un nouveau couple access + refresh."""
    return await auth_service.refresh(db, payload)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshRequest, db: DbSession):
    await auth_service.logout(db, payload)
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