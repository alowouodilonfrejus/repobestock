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
    """Repare l'enum PostgreSQL userrole sans perdre les donnees.

    - retire la valeur 'viewer' si presente (ancienne version)
    - ajoute la valeur 'EMPLOYE' si absente (nouveaux roles)

    Idempotent.
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
        if viewer is not None:
            manager = "MANAGER" if viewer.isupper() else "manager"
            await conn.execute(
                text("UPDATE users SET role = :manager WHERE role = :viewer"),
                {"manager": manager, "viewer": viewer},
            )
            await conn.execute(text("ALTER TYPE userrole RENAME TO userrole_old"))
            await conn.execute(
                text("CREATE TYPE userrole AS ENUM ('SUPERADMIN','ADMIN','MANAGER','EMPLOYE')")
            )
            await conn.execute(
                text(
                    "ALTER TABLE users ALTER COLUMN role "
                    "TYPE userrole USING role::text::userrole"
                )
            )
            await conn.execute(text("DROP TYPE userrole_old"))
            print("Enum userrole migre : valeur 'viewer' retiree.")
            return

        has_employe = any(label.lower() == "employe" for label in labels)
        if labels and not has_employe:
            await conn.execute(
                text("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'EMPLOYE'")
            )
            print("Enum userrole : valeur 'EMPLOYE' ajoutee.")


# Colonnes ajoutees au module de stock / affectations.
# Format : (nom_colonne, definition SQL complete)
_EQUIPEMENT_NEW_COLUMNS = [
    ("quantite", "INTEGER NOT NULL DEFAULT 1"),
    ("quantite_disponible", "INTEGER NOT NULL DEFAULT 1"),
    ("etat", "etatemateriel NOT NULL DEFAULT 'neuf'"),
    ("prix_achat", "NUMERIC(10, 2)"),
    (
        "fournisseur_id",
        "INTEGER REFERENCES fournisseurs(id) ON DELETE SET NULL",
    ),
]

_ENUMS = [
    ("etatemateriel", ["neuf", "tres_bon", "bon", "a_verifier", "endommage"]),
    (
        "statutaffectation",
        ["active", "partielle", "retournee", "annulee"],
    ),
    (
        "typemouvement",
        ["affectation", "retour", "entree", "sortie", "maintenance", "ajustement"],
    ),
    ("statutmaintenance", ["en_cours", "terminee"]),
]


async def _labels_de(conn, enum_name: str) -> list[str]:
    result = await conn.execute(
        text(
            "SELECT e.enumlabel FROM pg_enum e "
            "JOIN pg_type t ON t.oid = e.enumtypid "
            "WHERE t.typname = :nom ORDER BY e.enumsortorder"
        ),
        {"nom": enum_name},
    )
    return [row[0] for row in result]


async def migrate_stock_module() -> None:
    """Ajoute les colonnes/enums du module de stock a une base existante.

    Idempotent et auto-reparable : un enum existant avec des labels
    incorrects (ex. majuscules issues d'une version anterieure) est
    reconstruit ; les tables du module qui le référençaient sont vides
    et recreees juste apres.
    """
    async with engine.begin() as conn:
        for enum_name, labels in _ENUMS:
            existants = await _labels_de(conn, enum_name)
            if not existants:
                labels_sql = ", ".join(f"'{label}'" for label in labels)
                await conn.execute(
                    text(f"CREATE TYPE {enum_name} AS ENUM ({labels_sql})")
                )
                continue

            if existants == labels:
                continue

            # Labels incoherents : ne jamais DROP sans verifier que la table est vide.
            deps = await conn.execute(
                text(
                    "SELECT DISTINCT c.relname FROM pg_type t "
                    "JOIN pg_depend d ON d.refobjid = t.oid AND d.deptype = 'n' "
                    "JOIN pg_class c ON c.oid = d.objid "
                    "WHERE t.typname = :nom"
                ),
                {"nom": enum_name},
            )
            for (table,) in deps:
                if table not in ("equipements", "users"):
                    cnt = await conn.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                    row_count = cnt.scalar() or 0
                    if row_count > 0:
                        raise RuntimeError(
                            f"Migration enum {enum_name} bloque : table '{table}' "
                            f"contient {row_count} lignes avec labels incoherents {existants} != {labels}. "
                            "Migration manuelle requise (Alembic)."
                        )
                    await conn.execute(
                        text(f'DROP TABLE IF EXISTS "{table}" CASCADE')
                    )
                    print(f"Table '{table}' vide supprimee (enum a reparer).")
            await conn.execute(text(f"DROP TYPE {enum_name}"))
            labels_sql = ", ".join(f"'{label}'" for label in labels)
            await conn.execute(
                text(f"CREATE TYPE {enum_name} AS ENUM ({labels_sql})")
            )
            print(f"Enum {enum_name} reconstruit.")

        for column_name, definition in _EQUIPEMENT_NEW_COLUMNS:
            await conn.execute(
                text(
                    f"ALTER TABLE equipements "
                    f"ADD COLUMN IF NOT EXISTS {column_name} {definition}"
                )
            )

        # Recree les tables du module eventuellement supprimees ci-dessus.
        await conn.run_sync(Base.metadata.create_all)
    print("Module stock : migrations appliquees.")