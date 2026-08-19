from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.statut import Statut


async def list_statuts(db: AsyncSession) -> list[Statut]:
    result = await db.execute(
        select(Statut).where(Statut.actif.is_(True)).order_by(Statut.nom.asc())
    )
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, statut_id: int) -> Statut | None:
    return await db.get(Statut, statut_id)


async def get_by_nom(db: AsyncSession, nom: str) -> Statut | None:
    result = await db.execute(
        select(Statut).where(func.lower(Statut.nom) == nom.lower())
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, nom: str, description: str | None = None) -> Statut:
    statut = Statut(nom=nom, description=description, actif=True)
    db.add(statut)
    await db.commit()
    await db.refresh(statut)
    return statut
