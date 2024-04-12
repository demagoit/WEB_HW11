from fastapi import APIRouter, HTTPException, status, Path, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db
from src.database.schemas import RecordSchema, RecordUpdateSchema, RecordResponseSchema
from src.repository import contacts as rep_contacts

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/healthchecker')
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text('SELECT 1'))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail='Database is not configured corectly')
        return {'message': 'Welcome to Contacts app!'}
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail='Error connecting to database')


@router.get("/", response_model=list[RecordResponseSchema])
async def get_contacts(limit: int = Query(default=10, ge=1, le=50, description="Records per response to show"), 
                       offset: int = Query(
                           default=0, ge=0, description="Records to skip in response"),
                       db: AsyncSession = Depends(get_db)):
    result = await rep_contacts.get_contacts(limit=limit, offset=offset, db=db)
    return result


@router.get("/query", response_model=list[RecordResponseSchema])
async def get_contacts(first_name: str | None = Query(default=None, description="Pattern to search in First name"),
                       last_name: str | None = Query(
                           default=None, description="Pattern to search in Last name"),
                       email: str | None = Query(
                           default=None, description="Pattern to search in e-mail"),
                       days_to_birthday: int | None = Query(default=None, le=30, description="Filter contacts with birthday in given days"),
                       limit: int = Query(default=10, ge=1, le=50, description="Records per response to show"), 
                       offset: int = Query(default=0, ge=0, description="Records to skip in response"),
                       db: AsyncSession = Depends(get_db)):
    result = await rep_contacts.get_contacts_query(first_name=first_name, last_name=last_name, email=email, days_to_birthday=days_to_birthday,
                                                   limit=limit, offset=offset, db=db)
    return result


@router.get("/{rec_id}", response_model=RecordResponseSchema)
async def get_contact(rec_id: int = Path(description="ID of record to search"),
                      db: AsyncSession = Depends(get_db)):
    result = await rep_contacts.get_contact(record_id=rec_id, db=db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Record ID not found')
    return result


@router.post("/", response_model=RecordResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_contact(body: RecordSchema, db: AsyncSession = Depends(get_db)):
    result = await rep_contacts.create_contact(body=body, db=db)
    return result


@router.put("/{rec_id}", response_model=RecordResponseSchema)
async def update_contact(body: RecordSchema, rec_id: int = Path(description="ID of record to change"), db: AsyncSession = Depends(get_db)):
    result = await rep_contacts.update_contact(record_id=rec_id, body=body, db=db)
    return result


@router.delete("/{rec_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(rec_id: int = Path(description="ID of record to delete"), db: AsyncSession = Depends(get_db)):
    result = await rep_contacts.delete_contact(record_id=rec_id, db=db)
    return result
