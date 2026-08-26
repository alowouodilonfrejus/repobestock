from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fournisseur import Fournisseur


async def list_fournisseurs(
    db: AsyncSession,
) -> tuple[list[Fournisseur], int]:
    total = (
        await db.execute(select(func.count()).select_from(Fournisseur))
    ).scalar_one()
    result = await db.execute(select(Fournisseur).order_by(Fournisseur.nom))
    return list(result.scalars().all()), total


async def get_by_id(db: AsyncSession, fournisseur_id: int) -> Fournisseur | None:
    return await db.get(Fournisseur, fournisseur_id)


async def get_by_nom(db: AsyncSession, nom: str) -> Fournisseur | None:
    result = await db.execute(select(Fournisseur).where(Fournisseur.nom == nom))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, nom: str, contact: str | None = None) -> Fournisseur:
    fournisseur = Fournisseur(nom=nom, contact=contact)
    db.add(fournisseur)
    await db.commit()
    await db.refresh(fournisseur)
    return fournisseur
