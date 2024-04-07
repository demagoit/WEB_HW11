# import sys
# import os
# dir = os.path.split(os.path.dirname(__file__))
# # print(dir)
# sys.path.append(dir)

import contextlib
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from conf.config import config


class DatabaseSessionManager():
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url=url)
        self._sessionmaker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        if self._sessionmaker is None:
            raise Exception('db.py - Session is not initialized')
        session = self._sessionmaker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()




sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    with sessionmanager.session as session:
        yield session

# SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://admin:changeme@localhost:5432/rest_app"

# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
