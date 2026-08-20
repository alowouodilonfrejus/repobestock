import os

os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://postgres:postgres@db:5432/bestock_test"
)
os.environ["SECRET_KEY"] = "test-secret-key-avec-32-octets-minimum-0000"

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.init import create_tables, migrate_user_role
from app.db.seed import run_seed
from app.db.session import engine
from app.main import app

SUPERADMIN_EMAIL = "admin@bestock.dev"
SUPERADMIN_PASSWORD = "admin1234"


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _prepare_db():
    await create_tables()
    await migrate_user_role()
    await run_seed()
    yield
    await engine.dispose()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def auth_headers(client):
    resp = await client.post(
        "/api/v1/auth/login/json",
        json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}