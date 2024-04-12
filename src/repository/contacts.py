from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import datetime

from src.database.models import Record
from src.database.schemas import RecordSchema, RecordUpdateSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession):
    stmt = select(Record).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contacts_query(first_name: str | None, last_name: str | None, email: str | None, days_to_birthday: int | None, 
                             limit: int, offset: int, db: AsyncSession):
    filters = []

    if first_name:
        filters.append(f"first_name LIKE '%{first_name}%'")
    if last_name:
        filters.append(f"last_name LIKE '%{last_name}%'")
    if email:
        filters.append(f"email LIKE '%{email}%'")
    if days_to_birthday:
        filters.append(
            f"(birthday-DATE_TRUNC('year', birthday)+DATE_TRUNC('year', CURRENT_DATE)) <= CURRENT_DATE+{days_to_birthday}")

    if len(filters) > 0:
        sql_text = text(
            f'SELECT * FROM records WHERE {" AND ".join(filters)}  LIMIT {limit} OFFSET {offset};')
    else:
        sql_text = text(f'SELECT * FROM records LIMIT {limit} OFFSET {offset};')
    
    stmt = select(Record).from_statement(sql_text)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contact(record_id: int, db: AsyncSession):
    stmt = select(Record).filter_by(id=record_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_contact(body: RecordSchema, db: AsyncSession):
    rec = Record(**body.model_dump())
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec


async def update_contact(record_id: int, body: RecordSchema, db: AsyncSession):
    stmt = select(Record).filter_by(id=record_id)
    result = await db.execute(stmt)
    result = result.scalar_one_or_none()
    if result:
        result.first_name = body.first_name
        result.last_name = body.last_name
        result.email = body.email
        result.birthday = body.birthday
        result.notes = body.notes
        result.created_at = datetime.now()
        await db.commit()
        await db.refresh(result)
    return result


async def delete_contact(record_id: int, db: AsyncSession):
    stmt = select(Record).filter_by(id=record_id)
    result = await db.execute(stmt)
    result = result.scalar_one_or_none()
    if result:
        await db.delete(result)
        await db.commit()
    return result
