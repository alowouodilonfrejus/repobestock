import asyncio

from app.db.init import create_tables, migrate_stock_module, migrate_user_role
from app.db.seed import run_seed


async def main() -> None:
    await create_tables()
    await migrate_user_role()
    await migrate_stock_module()
    await run_seed()


if __name__ == "__main__":
    asyncio.run(main())