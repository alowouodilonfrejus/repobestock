from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class EmployeBase(BaseModel):
    nom_complet: str = Field(max_length=150)
    matricule: str = Field(max_length=50)
    departement: str | None = Field(default=None, max_length=100)
    fonction: str | None = Field(default=None, max_length=100)
    telephone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    date_arrivee: date | None = None
    actif: bool = True


class EmployeCreate(EmployeBase):
    user_id: int | None = None


class EmployeWithAccountCreate(EmployeBase):
    """Création d'un employé avec son compte de connexion en une seule requête."""

    username: str | None = Field(default=None, max_length=50, description="Nom d'utilisateur (défaut: partie avant @ de l'email)")
    password: str = Field(min_length=8, max_length=72, description="Mot de passe du compte employé (max 72 octets UTF-8, limite bcrypt)")
    role: str | None = Field(default="manager", description="Rôle du compte (manager par défaut)")

    @field_validator("password")
    @classmethod
    def _check_pw_bytes(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Mot de passe trop long : max 72 octets UTF-8")
        return v


class EmployeInscriptionCreate(BaseModel):
    """Inscription publique d'un employé : compte créé inactif, en attente de validation."""

    nom_complet: str = Field(max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    username: str | None = Field(default=None, max_length=50)
    matricule: str | None = Field(default=None, max_length=50)
    departement: str | None = Field(default=None, max_length=100)
    fonction: str | None = Field(default=None, max_length=100)
    telephone: str | None = Field(default=None, max_length=50)
    date_arrivee: date | None = None

    @field_validator("password")
    @classmethod
    def _check_pw_bytes(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Mot de passe trop long : max 72 octets UTF-8")
        return v


class EmployeUpdate(BaseModel):
    nom_complet: str | None = Field(default=None, max_length=150)
    matricule: str | None = Field(default=None, max_length=50)
    departement: str | None = Field(default=None, max_length=100)
    fonction: str | None = Field(default=None, max_length=100)
    telephone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    date_arrivee: date | None = None
    actif: bool | None = None


class EmployeRead(EmployeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    created_at: datetime
    updated_at: datetime


class MaterielAttribue(BaseModel):
    """Materiel actuellement sous la responsabilite d'un employe."""

    model_config = ConfigDict(from_attributes=True)

    affectation_item_id: int
    equipement_id: int
    reference: str
    nom: str
    quantite: int
    etat_affectation: str
    date_affectation: date
    date_retour_prevue: date | None
