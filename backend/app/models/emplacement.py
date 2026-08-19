from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Emplacement(Base):
    __tablename__ = "emplacements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    batiment: Mapped[str | None] = mapped_column(String(100), nullable=True)
    etage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    salle: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)

    equipements: Mapped[list["Equipement"]] = relationship(
        back_populates="emplacement"
    )
