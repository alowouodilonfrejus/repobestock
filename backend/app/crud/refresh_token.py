from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_refresh_token
from app.models.refresh_token import RefreshToken


def refresh_expiry() -> timedelta:
    return timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


async def create(db: AsyncSession, user_id: int, token: str) -> RefreshToken:
    refresh = RefreshToken(
        user_id=user_id,
        token_hash=hash_refresh_token(token),
        expires_at=datetime.now(timezone.utc) + refresh_expiry(),
    )
    db.add(refresh)
    await db.commit()
    await db.refresh(refresh)
    return refresh


async def get_by_token(db: AsyncSession, token: str) -> RefreshToken | None:
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(token)
        )
    )
    return result.scalar_one_or_none()


async def revoke(db: AsyncSession, refresh: RefreshToken) -> None:
    refresh.revoked = True
    await db.commit()


async def revoke_all_for_user(db: AsyncSession, user_id: int) -> None:
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked.is_(False),
        )
    )
    for refresh in result.scalars():
        refresh.revoked = True
    await db.commit()