from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def list_categories(db: AsyncSession) -> list[Category]:
    result = await db.execute(
        select(Category).order_by(Category.nom.asc())
    )
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, category_id: int) -> Category | None:
    return await db.get(Category, category_id)


async def get_by_nom(db: AsyncSession, nom: str) -> Category | None:
    result = await db.execute(
        select(Category).where(func.lower(Category.nom) == nom.lower())
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, payload: CategoryCreate) -> Category:
    category = Category(
        nom=payload.nom,
        description=payload.description,
        actif=payload.actif,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update(
    db: AsyncSession, category: Category, payload: CategoryUpdate
) -> Category:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category
