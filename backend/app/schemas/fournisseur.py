from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class FournisseurBase(BaseModel):
    nom: str = Field(max_length=100)
    contact: str | None = Field(default=None, max_length=100)
    telephone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None


class FournisseurCreate(FournisseurBase):
    pass


class FournisseurRead(FournisseurBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class FournisseurList(BaseModel):
    items: list[FournisseurRead]
    total: int
