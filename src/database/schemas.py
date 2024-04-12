from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date


class RecordSchema(BaseModel):
    first_name: str = Field(min_length=3, max_length=30)
    last_name: str | None = Field(min_length=0, max_length=30)
    email: str | None = Field(min_length=0, max_length=30)
    birthday: date | None = Field()
    notes: str | None = Field(min_length=0, max_length=150)


class RecordUpdateSchema(RecordSchema):
    pass


class RecordResponseSchema(BaseModel):
    id: int = 1
    first_name: str = "John"
    last_name: str | None = 'Doe'
    email: str | None
    birthday: date | None
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True