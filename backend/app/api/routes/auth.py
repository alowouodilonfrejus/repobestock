from fastapi import APIRouter, status

from app.api.deps import ActiveUser, DbSession
from app.schemas.token import LoginRequest, RefreshRequest, Token
from app.schemas.user import UserCreate, UserRead
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
async def register(payload: UserCreate, db: DbSession):
    return await auth_service.register(db, payload)


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


@router.get("/me", response_model=UserRead)
async def read_me(current_user: ActiveUser):
    return current_user