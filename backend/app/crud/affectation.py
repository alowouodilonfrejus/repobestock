from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.affectation import Affectation, AffectationItem, StatutAffectation
from app.models.equipement import Equipement


def _base_query():
    return select(Affectation).options(
        selectinload(Affectation.items).selectinload(AffectationItem.equipement),
        selectinload(Affectation.employe),
    )


async def list_affectations(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    employe_id: int | None = None,
    statut: str | None = None,
) -> tuple[list[Affectation], int]:
    stmt = _base_query()
    count_stmt = select(func.count()).select_from(Affectation)

    if employe_id is not None:
        stmt = stmt.where(Affectation.employe_id == employe_id)
        count_stmt = count_stmt.where(Affectation.employe_id == employe_id)
    if statut:
        stmt = stmt.where(Affectation.statut == statut)
        count_stmt = count_stmt.where(Affectation.statut == statut)

    total = (await db.execute(count_stmt)).scalar_one()
    stmt = stmt.order_by(Affectation.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().unique().all()), total


async def get_by_id(db: AsyncSession, affectation_id: int) -> Affectation | None:
    result = await db.execute(
        _base_query().where(Affectation.id == affectation_id)
    )
    return result.scalars().unique().one_or_none()


async def get_item_by_id(
    db: AsyncSession, affectation_item_id: int
) -> tuple[AffectationItem, Affectation] | None:
    """Renvoie (item, affectation_parente) ou None."""
    result = await db.execute(
        select(AffectationItem, Affectation)
        .join(Affectation, AffectationItem.affectation_id == Affectation.id)
        .where(AffectationItem.id == affectation_item_id)
    )
    row = result.first()
    return (row[0], row[1]) if row else None


async def count_active(db: AsyncSession) -> int:
    return (
        await db.execute(
            select(func.count())
            .select_from(Affectation)
            .where(Affectation.statut == StatutAffectation.ACTIVE)
        )
    ).scalar_one()


async def count_retours(db: AsyncSession) -> int:
    return (
        await db.execute(
            select(func.count())
            .select_from(Affectation)
            .where(
                Affectation.statut.in_(
                    [StatutAffectation.RETOURNEE, StatutAffectation.PARTIELLE]
                )
            )
        )
    ).scalar_one()
