from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.mouvement import TypeMouvement


class MouvementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipement_id: int
    equipement_reference: str
    equipement_nom: str
    employe_id: int | None
    employe_nom_complet: str | None
    user_id: int | None
    type: TypeMouvement
    quantite: int
    quantite_avant: int
    quantite_apres: int
    etat: str | None
    ref_type: str | None
    ref_id: int | None
    commentaire: str | None
    created_at: datetime


class MouvementList(BaseModel):
    items: list[MouvementRead]
    total: int
    limit: int
    skip: int
