from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models import User
from src.database.schemas import UserSchema


async def get_user_by_email(email: str, db: AsyncSession):
    stmt = select(User).filter_by(email=email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(body: UserSchema, db: AsyncSession):
    user = User(**body.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_token(user: User, token: str | None, db: AsyncSession):
    user.refresh_token = token
    await db.commit()
    await db.refresh(user)
    return user
