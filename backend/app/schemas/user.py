from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    username: str | None = None


MAX_PASSWORD_BYTES = 72


def _check_password_bytes(v: str | None) -> str | None:
    if v is not None and len(v.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise ValueError(f"Mot de passe trop long : max {MAX_PASSWORD_BYTES} octets UTF-8")
    return v


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    role: UserRole | None = None

    @field_validator("password")
    @classmethod
    def _check_pw_bytes(cls, v: str) -> str:
        return _check_password_bytes(v)


class UserAdminCreate(UserBase):
    password: str = Field(min_length=8)
    role: UserRole = UserRole.MANAGER

    @field_validator("password")
    @classmethod
    def _check_pw_bytes(cls, v: str) -> str:
        return _check_password_bytes(v)


class UserRead(UserBase):
    model_config = {"from_attributes": True}

    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    permissions: list[str] = []


class UserMeRead(UserRead):
    """Reponse /auth/me : user + permissions resolues cote serveur (source de verite)."""

    pass


class UserList(BaseModel):
    items: list[UserRead]
    total: int
    limit: int
    skip: int


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = Field(default=None, min_length=8)
    is_active: bool | None = None
    role: UserRole | None = None

    @field_validator("password")
    @classmethod
    def _check_pw_bytes(cls, v: str | None) -> str | None:
        return _check_password_bytes(v)


class UserValidation(BaseModel):
    """Validation d'une inscription en attente : activation + role final."""

    role: UserRole | None = None
