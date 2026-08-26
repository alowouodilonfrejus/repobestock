from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StatutMaintenance(str, Enum):
    EN_COURS = "en_cours"
    TERMINEE = "terminee"


class Maintenance(Base):
    __tablename__ = "maintenances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    equipement_id: Mapped[int] = mapped_column(
        ForeignKey("equipements.id"), nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    motif: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cout: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    technicien: Mapped[str | None] = mapped_column(String(100), nullable=True)
    statut: Mapped[StatutMaintenance] = mapped_column(
        SAEnum(
            StatutMaintenance,
            name="statutmaintenance",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=StatutMaintenance.EN_COURS,
    )
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
    )

    equipement = relationship("Equipement")  # noqa: F821

    @property
    def equipement_reference(self) -> str | None:
        return self.equipement.reference if self.equipement else None

    @property
    def equipement_nom(self) -> str | None:
        return self.equipement.nom if self.equipement else None
