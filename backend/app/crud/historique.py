from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.historique import Historique


async def list_historique(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Historique]:
    result = await db.execute(
        select(Historique)
        .options(selectinload(Historique.utilisateur))
        .order_by(Historique.date_action.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def list_for_equipement(
    db: AsyncSession, equipement_id: int
) -> list[Historique]:
    result = await db.execute(
        select(Historique)
        .options(selectinload(Historique.utilisateur))
        .where(Historique.equipement_id == equipement_id)
        .order_by(Historique.date_action.desc())
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    equipement_id: int,
    action: str,
    ancienne_valeur: str | None = None,
    nouvelle_valeur: str | None = None,
    utilisateur_id: int | None = None,
    adresse_ip: str | None = None,
) -> Historique:
    entree = Historique(
        utilisateur_id=utilisateur_id,
        equipement_id=equipement_id,
        action=action,
        ancienne_valeur=ancienne_valeur,
        nouvelle_valeur=nouvelle_valeur,
        adresse_ip=adresse_ip,
    )
    db.add(entree)
    await db.commit()
    await db.refresh(entree)
    return entree


async def create_no_commit(
    db: AsyncSession,
    equipement_id: int,
    action: str,
    ancienne_valeur: str | None = None,
    nouvelle_valeur: str | None = None,
    utilisateur_id: int | None = None,
    adresse_ip: str | None = None,
) -> Historique:
    """Ajoute une entree SANS commit : la transaction appartient au service.

    Utilisee par les operations critiques (affectations, retours, maintenance)
    ou plusieurs ecritures doivent reussir ou echouer ensemble.
    """
    entree = Historique(
        utilisateur_id=utilisateur_id,
        equipement_id=equipement_id,
        action=action,
        ancienne_valeur=ancienne_valeur,
        nouvelle_valeur=nouvelle_valeur,
        adresse_ip=adresse_ip,
    )
    db.add(entree)
    await db.flush()
    return entree
