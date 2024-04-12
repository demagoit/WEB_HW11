import contextlib
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from src.conf.config import config


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
            await session.rollback()
        finally:
            await session.close()


# print('---------------', config.DB_URL)

sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    async with sessionmanager.session() as session:
        yield session
