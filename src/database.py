from typing import Annotated, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from fastapi import Depends

from src.config import config

# Не создаём engine здесь, это будет сделано в функции ниже
engine = None
AsyncSessionLocal = None

class Base(DeclarativeBase):
    pass

def init_db(db_url: str = None):
    """Инициализация асинхронного подключения"""
    global engine, AsyncSessionLocal

    if db_url is None:
        db_url = config.db.url

    engine = create_async_engine(
        db_url,
        echo=False, # вывод логов в терминал
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False
    )

    return engine, AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Получить сессию БД"""
    if AsyncSessionLocal is None:
        init_db()

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def dispose() -> None:
    """Закрыть все соединения с БД"""
    global engine
    if engine is not None:
        await engine.dispose()
        engine = None

DbSessionDep = Annotated[AsyncSession, Depends(get_db)]