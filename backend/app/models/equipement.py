from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Equipement(Base):
    __tablename__ = "equipements"
    __table_args__ = (
        Index("ix_equipements_categorie_id", "categorie_id"),
        Index("ix_equipements_statut_id", "statut_id"),
        Index("ix_equipements_emplacement_id", "emplacement_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reference: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nom: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    marque: Mapped[str | None] = mapped_column(String(100), nullable=True)
    modele: Mapped[str | None] = mapped_column(String(100), nullable=True)
    numero_serie: Mapped[str | None] = mapped_column(
        String(150), unique=True, nullable=True
    )
    date_acquisition: Mapped[date | None] = mapped_column(Date, nullable=True)

    categorie_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    statut_id: Mapped[int] = mapped_column(
        ForeignKey("statuts.id"), nullable=False
    )
    emplacement_id: Mapped[int | None] = mapped_column(
        ForeignKey("emplacements.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
    )
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    categorie: Mapped["Category"] = relationship(back_populates="equipements")
    statut: Mapped["Statut"] = relationship(back_populates="equipements")
    emplacement: Mapped["Emplacement | None"] = relationship(
        back_populates="equipements"
    )
