from datetime import datetime

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    nom: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=10000)
    actif: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    nom: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=10000)
    actif: bool | None = None


class CategoryRead(CategoryBase):
    model_config = {"from_attributes": True}

    id: int
    created_at: datetime
    updated_at: datetime
