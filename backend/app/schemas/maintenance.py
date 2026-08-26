from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.maintenance import StatutMaintenance


class MaintenanceCreate(BaseModel):
    date_debut: date
    motif: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    cout: float | None = Field(default=None, ge=0, le=9999999999)
    technicien: str | None = Field(default=None, max_length=100)
    commentaire: str | None = Field(default=None, max_length=10000)


class MaintenanceCloture(BaseModel):
    date_fin: date | None = None
    commentaire: str | None = Field(default=None, max_length=10000)


class MaintenanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipement_id: int
    equipement_reference: str
    equipement_nom: str
    user_id: int | None
    date_debut: date
    date_fin: date | None
    motif: str | None
    description: str | None
    cout: float | None
    technicien: str | None
    statut: StatutMaintenance
    commentaire: str | None
    created_at: datetime


class MaintenanceList(BaseModel):
    items: list[MaintenanceRead]
    total: int
