from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.equipement import EtatMateriel
from app.models.affectation import StatutAffectation


class AffectationItemIn(BaseModel):
    """Ligne d'affectation : un materiel et sa quantite."""

    equipement_id: int
    quantite: int = Field(ge=1, le=1000000)
    etat_affectation: EtatMateriel = EtatMateriel.BON


class AffectationCreate(BaseModel):
    employe_id: int
    date_affectation: date | None = None
    date_retour_prevue: date | None = None
    motif: str | None = Field(default=None, max_length=200)
    commentaire: str | None = Field(default=None, max_length=10000)
    items: list[AffectationItemIn] = Field(min_length=1)


class RetourItemIn(BaseModel):
    affectation_item_id: int
    quantite_retournee: int = Field(ge=1, le=1000000)
    etat_retour: EtatMateriel
    accessoires_retournes: str | None = Field(default=None, max_length=10000)
    probleme_constate: str | None = Field(default=None, max_length=10000)
    commentaire: str | None = Field(default=None, max_length=10000)


class RetourCreate(BaseModel):
    date_retour: date | None = None
    items: list[RetourItemIn] = Field(min_length=1)
    commentaire: str | None = Field(default=None, max_length=10000)


class AffectationItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipement_id: int
    equipement_reference: str
    equipement_nom: str
    quantite: int
    etat_affectation: str
    quantite_retournee: int
    etat_retour: str | None
    accessoires_retournes: str | None
    probleme_constate: str | None
    date_retour: date | None
    commentaire: str | None


class AffectationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employe_id: int
    employe_nom_complet: str
    employe_matricule: str
    cree_par: int
    date_affectation: date
    date_retour_prevue: date | None
    motif: str | None
    commentaire: str | None
    statut: StatutAffectation
    created_at: datetime
    items: list[AffectationItemRead]


class AffectationList(BaseModel):
    items: list[AffectationRead]
    total: int
    limit: int
    skip: int
