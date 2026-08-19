from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Historique(Base):
    __tablename__ = "historique"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    utilisateur_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    equipement_id: Mapped[int | None] = mapped_column(
        ForeignKey("equipements.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    ancienne_valeur: Mapped[str | None] = mapped_column(Text, nullable=True)
    nouvelle_valeur: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_action: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    adresse_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)

    utilisateur: Mapped["User | None"] = relationship()

    @property
    def utilisateur_nom(self) -> str | None:
        if self.utilisateur is not None:
            return self.utilisateur.username or self.utilisateur.email
        return None
