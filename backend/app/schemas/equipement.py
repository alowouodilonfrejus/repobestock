from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.equipement import EtatMateriel


class EquipementBase(BaseModel):
    reference: str = Field(max_length=50)
    nom: str = Field(max_length=150)
    description: str | None = Field(default=None, max_length=10000)
    marque: str | None = Field(default=None, max_length=100)
    modele: str | None = Field(default=None, max_length=100)
    numero_serie: str | None = Field(default=None, max_length=150)
    date_acquisition: date | None = None
    quantite: int = Field(default=1, ge=1, le=1000000)
    etat: EtatMateriel = EtatMateriel.NEUF
    prix_achat: float | None = Field(default=None, ge=0, le=9999999999)
    fournisseur_id: int | None = None
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
    quantite: int | None = Field(default=None, ge=1, le=1000000)
    etat: EtatMateriel | None = None
    prix_achat: float | None = Field(default=None, ge=0, le=9999999999)
    fournisseur_id: int | None = None
    categorie_id: int | None = None
    statut_id: int | None = None
    emplacement_id: int | None = None


class EquipementRead(EquipementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantite_disponible: int
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
    # Indicateurs du module de stock / affectations (optionnels pour
    # compatibilite ascendante avec l'ancien dashboard).
    disponibles: int = 0
    affectes: int = 0
    endommages: int = 0
    perdus: int = 0
    hors_service: int = 0
    affectations_actives: int = 0
    retours_total: int = 0
    affectations_recentes: list["AffectationResume"] = []


class AffectationResume(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employe_nom: str
    nombre_items: int
    statut: str
    date_affectation: date


EquipementStats.model_rebuild()
