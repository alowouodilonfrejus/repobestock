from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.emplacement import Emplacement


async def list_emplacements(db: AsyncSession) -> list[Emplacement]:
    result = await db.execute(
        select(Emplacement)
        .where(Emplacement.actif.is_(True))
        .order_by(Emplacement.nom.asc())
    )
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, emplacement_id: int) -> Emplacement | None:
    return await db.get(Emplacement, emplacement_id)


async def get_by_nom(db: AsyncSession, nom: str) -> Emplacement | None:
    result = await db.execute(
        select(Emplacement).where(func.lower(Emplacement.nom) == nom.lower())
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, nom: str) -> Emplacement:
    emplacement = Emplacement(nom=nom, actif=True)
    db.add(emplacement)
    await db.commit()
    await db.refresh(emplacement)
    return emplacement
