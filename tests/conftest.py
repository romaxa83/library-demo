import sys
from pathlib import Path
from faker import Faker

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from alembic.config import Config as AlembicConfig
from alembic import command

from src.config import Config
from src.database import Base
from src.main import app
from src.books import dependencies

# Используем тестовую БД конфигурацию
test_config = Config()
test_db_config = test_config.test_db


@pytest.fixture(scope="session")
def test_database_url():
    """Возвращает URL тестовой БД"""
    return test_db_config.url


def run_migrations(database_url: str):
    """Запустить миграции Alembic на указанную БД"""
    alembic_config = AlembicConfig("alembic.ini")
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


@pytest.fixture(scope="session")
def engine(test_database_url):
    """Создает engine для тестовой БД и запускает миграции"""
    engine = create_engine(
        test_database_url,
        echo=False,
        pool_pre_ping=True,
    )

    # Проверяем, есть ли таблицы
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if not existing_tables:
        # print(f"📋 В тестовой БД нет таблиц. Запускаем миграции...")
        # Запускаем миграции на тестовую БД
        run_migrations(test_database_url)
    else:
        print(f"✅ В тестовой БД найдены таблицы: {existing_tables}")

    # Дополнительная проверка, что таблицы созданы
    inspector = inspect(engine)
    if "authors" not in inspector.get_table_names():
        # print("❌ Таблица 'authors' не найдена! Пробуем создать вручную...")
        Base.metadata.create_all(bind=engine)

    yield engine

    # Не удаляем таблицы после тестов, оставляем их для отладки
    # Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Создает новую сессию БД для каждого теста"""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Создает TestClient с переопределённой зависимостью get_session"""

    def override_get_session():
        try:
            yield db_session
        finally:
            pass

    # Переопределяем get_session, а не get_db
    app.dependency_overrides[dependencies.get_session] = override_get_session

    yield TestClient(app)

    app.dependency_overrides.clear()

# Импортируем фикстуры из папки fixtures
pytest_plugins = [
    "tests.fixtures.base",
    "tests.fixtures.author",
    "tests.fixtures.book",
]