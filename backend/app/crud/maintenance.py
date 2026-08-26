from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.maintenance import Maintenance, StatutMaintenance


async def list_maintenances(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    equipement_id: int | None = None,
) -> tuple[list[Maintenance], int]:
    stmt = select(Maintenance).options(selectinload(Maintenance.equipement))
    count_stmt = select(func.count()).select_from(Maintenance)

    if equipement_id is not None:
        stmt = stmt.where(Maintenance.equipement_id == equipement_id)
        count_stmt = count_stmt.where(Maintenance.equipement_id == equipement_id)

    total = (await db.execute(count_stmt)).scalar_one()
    stmt = stmt.order_by(Maintenance.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().unique().all()), total


async def get_by_id(db: AsyncSession, maintenance_id: int) -> Maintenance | None:
    result = await db.execute(
        select(Maintenance)
        .options(selectinload(Maintenance.equipement))
        .where(Maintenance.id == maintenance_id)
    )
    return result.scalars().one_or_none()


async def get_en_cours(
    db: AsyncSession, equipement_id: int
) -> Maintenance | None:
    """Maintenance non terminee pour un materiel (max une a la fois)."""
    result = await db.execute(
        select(Maintenance).where(
            Maintenance.equipement_id == equipement_id,
            Maintenance.statut == StatutMaintenance.EN_COURS,
        )
    )
    return result.scalar_one_or_none()


async def list_for_user(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> tuple[list[Maintenance], int]:
    """Maintenances des materiels affectes (ou ayant ete affectes)
    au collaborateur rattache au compte utilisateur donne."""
    from app.models.affectation import Affectation
    from app.models.affectation import AffectationItem
    from app.models.employe import Employe

    sous_requete = (
        select(AffectationItem.equipement_id)
        .join(Affectation, AffectationItem.affectation_id == Affectation.id)
        .join(Employe, Affectation.employe_id == Employe.id)
        .where(Employe.user_id == user_id)
        .scalar_subquery()
    )
    stmt = (
        select(Maintenance)
        .options(selectinload(Maintenance.equipement))
        .where(Maintenance.equipement_id.in_(sous_requete))
    )
    count_stmt = select(func.count()).select_from(Maintenance).where(
        Maintenance.equipement_id.in_(sous_requete)
    )
    total = (await db.execute(count_stmt)).scalar_one()
    stmt = stmt.order_by(Maintenance.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().unique().all()), total
