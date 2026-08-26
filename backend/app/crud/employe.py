from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employe import Employe


async def list_employes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    actif: bool | None = None,
) -> tuple[list[Employe], int]:
    stmt = select(Employe)
    count_stmt = select(func.count()).select_from(Employe)
    if actif is not None:
        stmt = stmt.where(Employe.actif == actif)
        count_stmt = count_stmt.where(Employe.actif == actif)

    total = (await db.execute(count_stmt)).scalar_one()
    stmt = stmt.order_by(Employe.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def get_by_id(db: AsyncSession, employe_id: int) -> Employe | None:
    return await db.get(Employe, employe_id)


async def get_by_matricule(db: AsyncSession, matricule: str) -> Employe | None:
    result = await db.execute(
        select(Employe).where(Employe.matricule == matricule)
    )
    return result.scalar_one_or_none()


async def get_by_user_id(db: AsyncSession, user_id: int) -> Employe | None:
    result = await db.execute(
        select(Employe).where(Employe.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, employe: Employe) -> Employe:
    db.add(employe)
    await db.commit()
    await db.refresh(employe)
    return employe


async def delete(db: AsyncSession, employe: Employe) -> None:
    await db.delete(employe)
    await db.commit()
