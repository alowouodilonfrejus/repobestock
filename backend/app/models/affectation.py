from datetime import date, datetime
from enum import Enum

from sqlalchemy import (
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StatutAffectation(str, Enum):
    ACTIVE = "active"
    PARTIELLE = "partielle"
    RETOURNEE = "retournee"
    ANNULEE = "annulee"


class Affectation(Base):
    __tablename__ = "affectations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employe_id: Mapped[int] = mapped_column(
        ForeignKey("employes.id"), nullable=False
    )
    cree_par: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    date_affectation: Mapped[date] = mapped_column(Date, nullable=False)
    date_retour_prevue: Mapped[date | None] = mapped_column(Date, nullable=True)
    motif: Mapped[str | None] = mapped_column(String(200), nullable=True)
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)
    statut: Mapped[StatutAffectation] = mapped_column(
        SAEnum(
            StatutAffectation,
            name="statutaffectation",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=StatutAffectation.ACTIVE,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
    )

    employe: Mapped["Employe"] = relationship(back_populates="affectations")  # noqa: F821
    items: Mapped[list["AffectationItem"]] = relationship(
        back_populates="affectation", cascade="all, delete-orphan"
    )

    @property
    def employe_nom_complet(self) -> str | None:
        return self.employe.nom_complet if self.employe else None

    @property
    def employe_matricule(self) -> str | None:
        return self.employe.matricule if self.employe else None


class AffectationItem(Base):
    __tablename__ = "affectation_items"
    __table_args__ = (Index("ix_affectation_items_equipement_id", "equipement_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    affectation_id: Mapped[int] = mapped_column(
        ForeignKey("affectations.id"), nullable=False
    )
    equipement_id: Mapped[int] = mapped_column(
        ForeignKey("equipements.id"), nullable=False
    )
    quantite: Mapped[int] = mapped_column(Integer, nullable=False)
    etat_affectation: Mapped[str] = mapped_column(String(30), nullable=False)
    quantite_retournee: Mapped[int] = mapped_column(Integer, default=0)
    etat_retour: Mapped[str | None] = mapped_column(String(30), nullable=True)
    accessoires_retournes: Mapped[str | None] = mapped_column(Text, nullable=True)
    probleme_constate: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_retour: Mapped[date | None] = mapped_column(Date, nullable=True)
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)

    affectation: Mapped[Affectation] = relationship(back_populates="items")
    equipement = relationship("Equipement")  # noqa: F821

    @property
    def equipement_reference(self) -> str | None:
        return self.equipement.reference if self.equipement else None

    @property
    def equipement_nom(self) -> str | None:
        return self.equipement.nom if self.equipement else None
