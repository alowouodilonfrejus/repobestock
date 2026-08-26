from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.mouvement import Mouvement


async def list_mouvements(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    equipement_id: int | None = None,
) -> tuple[list[Mouvement], int]:
    stmt = select(Mouvement).options(
        selectinload(Mouvement.equipement),
        selectinload(Mouvement.employe),
    )
    count_stmt = select(func.count()).select_from(Mouvement)

    if equipement_id is not None:
        stmt = stmt.where(Mouvement.equipement_id == equipement_id)
        count_stmt = count_stmt.where(Mouvement.equipement_id == equipement_id)

    total = (await db.execute(count_stmt)).scalar_one()
    stmt = stmt.order_by(Mouvement.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().unique().all()), total


async def create(db: AsyncSession, mouvement: Mouvement) -> Mouvement:
    """Ajoute un mouvement SANS commit : la transaction appartient au service."""
    db.add(mouvement)
    await db.flush()
    await db.refresh(mouvement)
    return mouvement
