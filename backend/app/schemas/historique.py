from datetime import datetime

from pydantic import BaseModel, Field
from pydantic.functional_serializers import field_serializer


class HistoriqueRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    utilisateur_id: int | None
    utilisateur_nom: str | None = None
    equipement_id: int | None
    action: str
    ancienne_valeur: str | None
    nouvelle_valeur: str | None
    date_action: datetime
    adresse_ip: str | None

    @field_serializer("utilisateur_nom")
    def _utilisateur_nom(self, value: str | None, _info) -> str | None:
        return value or "Utilisateur inconnu"


class HistoriqueCreate(BaseModel):
    equipement_id: int
    action: str
    ancienne_valeur: str | None = None
    nouvelle_valeur: str | None = None
