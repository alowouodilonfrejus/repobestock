import asyncio

from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine


async def create_tables() -> None:
    """Cree les tables si elles n'existent pas, avec nouvelle sur base non prete."""
    max_retries = 10
    for i in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("Tables creees.")
            return
        except Exception as e:
            print(
                f"Erreur lors de la creation des tables (tentative {i+1}/{max_retries}) : {e}"
            )
            if i == max_retries - 1:
                raise
            await asyncio.sleep(3)


async def migrate_user_role() -> None:
    """Retire la valeur 'viewer' de l'enum PostgreSQL userrole sans perdre les donnees.

    Idempotent : ne fait rien si 'viewer' n'est pas present dans l'enum.
    """
    async with engine.begin() as conn:
        try:
            result = await conn.execute(
                text(
                    "SELECT enumlabel FROM pg_enum e "
                    "JOIN pg_type t ON t.oid = e.enumtypid "
                    "WHERE t.typname = 'userrole'"
                )
            )
            labels = [row[0] for row in result]
        except Exception:
            labels = []

        viewer = next((label for label in labels if label.lower() == "viewer"), None)
        if viewer is None:
            return

        manager = "MANAGER" if viewer.isupper() else "manager"
        await conn.execute(
            text(f"UPDATE users SET role = '{manager}' WHERE role = '{viewer}'")
        )
        await conn.execute(text("ALTER TYPE userrole RENAME TO userrole_old"))
        await conn.execute(
            text("CREATE TYPE userrole AS ENUM ('SUPERADMIN','ADMIN','MANAGER')")
        )
        await conn.execute(
            text(
                "ALTER TABLE users ALTER COLUMN role "
                "TYPE userrole USING role::text::userrole"
            )
        )
        await conn.execute(text("DROP TYPE userrole_old"))
        print("Enum userrole migre : valeur 'viewer' retiree.")