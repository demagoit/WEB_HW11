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
async def get_contacts(limit: int = Query(default=10, ge=1, le=50), offset: int = Query(default=0, ge=0), db: AsyncSession = Depends(get_db)):
    result = rep_contacts.get_contacts(limit=limit, offset=offset, db=db)
    return result


@router.get("/{rec_id}", response_model=RecordResponseSchema)
async def get_contact(rec_id: int, db: AsyncSession = Depends(get_db)):
    result = await rep_contacts.get_contact(record_id=rec_id, db=db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Record ID not found')


@router.post("/", response_model=RecordResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_contact(body: RecordSchema, db: AsyncSession = Depends(get_db)):
    result = await rep_contacts.create_contact(body=body, db=db)
    return result


@router.put("/{id:int}", response_model=RecordUpdateSchema)
async def update_contact(id):
    pass


@router.delete("/{id:int}")
async def delete_contact(id):
    pass
