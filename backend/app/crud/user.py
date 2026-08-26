from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate


async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def get_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()


async def list_users(
    db: AsyncSession, skip: int = 0, limit: int = 50
) -> tuple[list[User], int]:
    count_stmt = select(func.count()).select_from(User)
    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all()), total


async def create(
    db: AsyncSession,
    payload: UserCreate,
    role: UserRole = UserRole.MANAGER,
    is_active: bool = True,
) -> User:
    email = payload.email.lower()
    user = User(
        email=email,
        username=payload.username or email.split("@")[0],
        hashed_password=hash_password(payload.password),
        role=role,
        is_active=is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update(db: AsyncSession, user: User, data: dict) -> User:
    if "password" in data and data["password"]:
        user.hashed_password = hash_password(data.pop("password"))
    else:
        data.pop("password", None)

    for field, value in data.items():
        setattr(user, field, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()


async def authenticate(
    db: AsyncSession, email: str, password: str
) -> User | None:
    user = await get_by_email(db, email.lower())
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
