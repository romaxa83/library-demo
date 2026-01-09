import sys
import os
from pathlib import Path
import asyncio

from httpx import AsyncClient, ASGITransport

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from alembic.config import Config as AlembicConfig
from alembic import command

from src.config import config, BASE_DIR
from src.database import Base, get_db
from src.main import app
from dotenv import load_dotenv

# Загружаем тестовый конфиг принудительно в самом начале
load_dotenv(".env.testing", override=True)

# @pytest.fixture(scope="session")
# def event_loop():
#     """Создает event loop для всей тестовой сессии"""
#     loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()


def run_migrations(database_url: str):
    """Запустить миграции Alembic на указанную БД"""

    # миграции запускаются с тестов, нужно правильный путь к alembic.ini
    base_dir = BASE_DIR
    ini_path = os.path.join(base_dir, "alembic.ini")
    ini_path = os.path.abspath(ini_path)

    alembic_config = AlembicConfig(ini_path)
    alembic_config.set_main_option("sqlalchemy.url", database_url)

    try:
        # Проверяем, есть ли уже миграции
        command.current(alembic_config)
        # Если мы здесь, то есть история миграций, обновляем до head
        # print("📦 Обновляем миграции до последней версии...")
        command.upgrade(alembic_config, "head")
        # print("✅ Миграции успешно выполнены!")
    except Exception as e:
        print(f"⚠️  Ошибка при запуске миграций: {e}")
        # print("📋 Создаём таблицы вручную через SQLAlchemy...")
        raise

@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Создает асинхронный engine для тестовой БД"""
    # Убедитесь, что URL в .env.testing начинается с postgresql+asyncpg://
    engine = create_async_engine(
        config.db.url,
        echo=False,
        pool_pre_ping=True,
    )

    async with engine.begin() as conn:
        # Создаем таблицы асинхронно
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine):
    """Создает изолированную сессию через вложенную транзакцию"""
    connection = await test_engine.connect()
    # Начинаем внешнюю транзакцию
    trans = await connection.begin()

    # Создаем сессию, привязанную к этому соединению
    async_session = AsyncSession(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint"  # Магия здесь: commit станет savepoint
    )

    yield async_session

    # Откатываем внешнюю транзакцию - это удалит ВСЕ данные, созданные в тесте
    await async_session.close()
    await trans.rollback()
    await connection.close()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Создает AsyncClient для тестов"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Используем AsyncClient с транспортом приложения
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

# Импортируем фикстуры из папки fixtures
pytest_plugins = [
    "tests.fixtures.base",
    "tests.fixtures.author",
    "tests.fixtures.book",
    "tests.fixtures.user",
    "tests.fixtures.role",
    "tests.fixtures.permission",
]