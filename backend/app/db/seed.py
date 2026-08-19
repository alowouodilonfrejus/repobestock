from app.core.config import settings
from app.core.security import hash_password
from app.crud import category as crud_category
from app.crud import emplacement as crud_emplacement
from app.crud import statut as crud_statut
from app.crud import user as crud_user
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.schemas.category import CategoryCreate

DEFAULT_CATEGORIES = [
    {"nom": "Informatique", "description": "Ordinateurs, serveurs, peripheriques"},
    {"nom": "Immobilier", "description": "Equipements immobiliers, batiment et mobilier de bureau"},
    {"nom": "Nettoyage", "description": "Materiel de nettoyage et entretien"},
]

DEFAULT_STATUTS = [
    {"nom": "Fonctionnel", "description": "Operationnel et disponible"},
    {"nom": "Defectueux", "description": "Hors service"},
    {"nom": "En maintenance", "description": "Envoye en maintenance"},
]

DEFAULT_EMPLACEMENTS = [
    {"nom": "Entrepot"},
    {"nom": "Bureau"},
]


async def seed_superadmin() -> None:
    async with AsyncSessionLocal() as db:
        existing = await crud_user.get_by_email(
            db, settings.FIRST_SUPERUSER_EMAIL
        )
        if existing:
            print(f"Super admin deja present : {existing.email}")
            return

        user = User(
            email=settings.FIRST_SUPERUSER_EMAIL.lower(),
            username=settings.FIRST_SUPERUSER_USERNAME,
            hashed_password=hash_password(settings.FIRST_SUPERUSER_PASSWORD),
            role=UserRole.SUPERADMIN,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        print(f"Super admin cree : {user.email}")


async def seed_categories() -> None:
    async with AsyncSessionLocal() as db:
        for item in DEFAULT_CATEGORIES:
            existing = await crud_category.get_by_nom(db, item["nom"])
            if existing:
                continue
            await crud_category.create(
                db,
                CategoryCreate(
                    nom=item["nom"], description=item["description"]
                ),
            )
            print(f"Categorie creee : {item['nom']}")


async def seed_statuts() -> None:
    async with AsyncSessionLocal() as db:
        for item in DEFAULT_STATUTS:
            existing = await crud_statut.get_by_nom(db, item["nom"])
            if existing:
                continue
            await crud_statut.create(db, item["nom"], item["description"])
            print(f"Statut cree : {item['nom']}")


async def seed_emplacements() -> None:
    async with AsyncSessionLocal() as db:
        for item in DEFAULT_EMPLACEMENTS:
            existing = await crud_emplacement.get_by_nom(db, item["nom"])
            if existing:
                continue
            await crud_emplacement.create(db, item["nom"])
            print(f"Emplacement cree : {item['nom']}")


async def run_seed() -> None:
    await seed_superadmin()
    await seed_categories()
    await seed_statuts()
    await seed_emplacements()
    print("Seed termine.")