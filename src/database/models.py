from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func, Date
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


# class Record(Base):
#     __tablename__ = "records"
#     id = Column(Integer, primary_key=True)
#     first_name = Column(String(30), nullable=False)
#     last_name = Column(String(30))
#     email = Column(String(30))
#     birthday = Column(Date)
#     notes = Column(String(150))
#     created_at = Column(DateTime, default=func.now())


class Record(Base):
    __tablename__ = "records"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(30), index=True)
    email: Mapped[str] = mapped_column(String(30), index=True)
    birthday: Mapped[Date] = mapped_column(Date)
    notes: Mapped[str] = mapped_column(String(150))
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())