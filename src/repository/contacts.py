from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models import Record
from src.database.schemas import RecordSchema, RecordUpdateSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession):
    stmt = select(Record).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contact(record_id: int, db: AsyncSession):
    stmt = select(Record).filter_by(id=record_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_contact(body: RecordSchema, db: AsyncSession):
    rec = Record(**body.model_dump(exclude_unset=True))
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec


async def update_contact(record_id: int, db: AsyncSession):
    pass


async def delete_contact(record_id: int, db: AsyncSession):
    pass
