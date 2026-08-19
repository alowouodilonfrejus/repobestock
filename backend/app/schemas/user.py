from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    username: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    role: UserRole | None = None


class UserAdminCreate(UserBase):
    password: str = Field(min_length=8)
    role: UserRole = UserRole.MANAGER


class UserRead(UserBase):
    model_config = {"from_attributes": True}

    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


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
