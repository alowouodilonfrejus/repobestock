from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Employe(Base):
    __tablename__ = "employes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nom_complet: Mapped[str] = mapped_column(String(150), nullable=False)
    matricule: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    departement: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fonction: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    date_arrivee: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Lien optionnel vers un compte utilisateur : permet a l'employe de
    # consulter les materiels qui lui sont attribues.
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
    )

    affectations: Mapped[list["Affectation"]] = relationship(  # noqa: F821
        back_populates="employe"
    )
