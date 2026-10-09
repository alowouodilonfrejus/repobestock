from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    # Optionnel : le refresh token peut venir du cookie httpOnly
    # (frontend) ou du corps JSON (clients API / tests)
    refresh_token: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str