from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TypeMouvement(str, Enum):
    AFFECTATION = "affectation"
    RETOUR = "retour"
    ENTREE = "entree"
    SORTIE = "sortie"
    MAINTENANCE = "maintenance"
    AJUSTEMENT = "ajustement"


class Mouvement(Base):
    """Mouvement de stock : chaque operation sur un materiel y est tracee.

    Insertion seule : aucun endpoint ne modifie ou supprime un mouvement,
    afin de garantir une timeline fiable par materiel.
    """

    __tablename__ = "mouvements"
    __table_args__ = (Index("ix_mouvements_equipement_id", "equipement_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    equipement_id: Mapped[int] = mapped_column(
        ForeignKey("equipements.id"), nullable=False
    )
    employe_id: Mapped[int | None] = mapped_column(
        ForeignKey("employes.id"), nullable=True
    )
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    type: Mapped[TypeMouvement] = mapped_column(
        SAEnum(
            TypeMouvement,
            name="typemouvement",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    quantite: Mapped[int] = mapped_column(Integer, default=1)
    quantite_avant: Mapped[int] = mapped_column(Integer, nullable=False)
    quantite_apres: Mapped[int] = mapped_column(Integer, nullable=False)
    etat: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ref_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ref_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    equipement = relationship("Equipement")  # noqa: F821
    employe = relationship("Employe")  # noqa: F821

    @property
    def equipement_reference(self) -> str | None:
        return self.equipement.reference if self.equipement else None

    @property
    def equipement_nom(self) -> str | None:
        return self.equipement.nom if self.equipement else None

    @property
    def employe_nom_complet(self) -> str | None:
        return self.employe.nom_complet if self.employe else None
