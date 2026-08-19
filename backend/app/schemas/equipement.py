from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class EquipementBase(BaseModel):
    reference: str = Field(max_length=50)
    nom: str = Field(max_length=150)
    description: str | None = Field(default=None, max_length=10000)
    marque: str | None = Field(default=None, max_length=100)
    modele: str | None = Field(default=None, max_length=100)
    numero_serie: str | None = Field(default=None, max_length=150)
    date_acquisition: date | None = None
    categorie_id: int
    statut_id: int
    emplacement_id: int | None = None


class EquipementCreate(EquipementBase):
    pass


class EquipementUpdate(BaseModel):
    reference: str | None = Field(default=None, max_length=50)
    nom: str | None = Field(default=None, max_length=150)
    description: str | None = Field(default=None, max_length=10000)
    marque: str | None = Field(default=None, max_length=100)
    modele: str | None = Field(default=None, max_length=100)
    numero_serie: str | None = Field(default=None, max_length=150)
    date_acquisition: date | None = None
    categorie_id: int | None = None
    statut_id: int | None = None
    emplacement_id: int | None = None


class EquipementRead(EquipementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class EquipementList(BaseModel):
    items: list[EquipementRead]
    total: int
    limit: int
    skip: int


class EquipementStats(BaseModel):
    total: int
    maintenance: int
    recent: list[EquipementRead]
