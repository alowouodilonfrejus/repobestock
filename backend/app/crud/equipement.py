from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.equipement import Equipement
from app.schemas.equipement import EquipementCreate, EquipementUpdate


async def list_equipements(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    categorie_id: int | None = None,
) -> tuple[list[Equipement], int]:
    stmt = select(Equipement)
    count_stmt = select(func.count()).select_from(Equipement)

    if categorie_id is not None:
        stmt = stmt.where(Equipement.categorie_id == categorie_id)
        count_stmt = count_stmt.where(Equipement.categorie_id == categorie_id)

    total = (await db.execute(count_stmt)).scalar_one()
    stmt = stmt.order_by(Equipement.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def list_recent(db: AsyncSession, limit: int = 8) -> list[Equipement]:
    result = await db.execute(
        select(Equipement)
        .order_by(Equipement.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def count_total(db: AsyncSession) -> int:
    return (
        await db.execute(select(func.count()).select_from(Equipement))
    ).scalar_one()


async def count_by_statut(db: AsyncSession, statut_id: int) -> int:
    return (
        await db.execute(
            select(func.count())
            .select_from(Equipement)
            .where(Equipement.statut_id == statut_id)
        )
    ).scalar_one()


async def get_by_id(db: AsyncSession, equipement_id: int) -> Equipement | None:
    return await db.get(Equipement, equipement_id)


async def get_by_reference(
    db: AsyncSession, reference: str
) -> Equipement | None:
    result = await db.execute(
        select(Equipement).where(Equipement.reference == reference)
    )
    return result.scalar_one_or_none()


async def get_by_numero_serie(
    db: AsyncSession, numero_serie: str
) -> Equipement | None:
    result = await db.execute(
        select(Equipement).where(Equipement.numero_serie == numero_serie)
    )
    return result.scalar_one_or_none()


async def create(
    db: AsyncSession, payload: EquipementCreate, user_id: int | None = None
) -> Equipement:
    equipement = Equipement(**payload.model_dump())
    equipement.created_by = user_id
    # A la creation, tout le stock est disponible.
    equipement.quantite_disponible = payload.quantite
    db.add(equipement)
    await db.commit()
    await db.refresh(equipement)
    return equipement


async def update(
    db: AsyncSession,
    equipement: Equipement,
    payload: EquipementUpdate,
    user_id: int | None = None,
) -> Equipement:
    data = payload.model_dump(exclude_unset=True)
    # Si le stock total change, la disponibilite suit le meme delta.
    if "quantite" in data and data["quantite"] != equipement.quantite:
        delta = data["quantite"] - equipement.quantite
        equipement.quantite_disponible = max(
            0, equipement.quantite_disponible + delta
        )
    for key, value in data.items():
        setattr(equipement, key, value)
    equipement.updated_by = user_id
    db.add(equipement)
    await db.commit()
    await db.refresh(equipement)
    return equipement


async def delete(db: AsyncSession, equipement: Equipement) -> None:
    await db.delete(equipement)
    await db.commit()
