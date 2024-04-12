from pydantic import BaseModel, Field, EmailStr


class RecordSchema(BaseModel):
    first_name: str = Field(min_length=3, max_length=30)
    last_name: str = Field(min_length=0, max_length=30)
    email: str = Field(min_length=0, max_length=30)
    birthday: str = Field(min_length=0, max_length=30)
    notes: str = Field(min_length=0, max_length=150)


class RecordUpdateSchema(RecordSchema):
    pass


class RecordResponseSchema(BaseModel):
    id: int = 1
    first_name: str
    last_name: str
    email: str
    birthday: str
    notes: str
    # created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    class Config:
        from_attributes = True