import pytest_asyncio
from faker import Faker

from src.books.models import Author

@pytest_asyncio.fixture
def fake():
    """Фикстура для генерации фейковых данных"""
    return Faker()


@pytest_asyncio.fixture
async def author_factory(db_session, fake):
    """Фабрика для создания тестовых авторов"""

    async def create(**kwargs):
        author = Author(
            name=kwargs.get("name") or fake.name(),
            description=kwargs.get("description") or fake.text(max_nb_chars=200),
            deleted_at=kwargs.get("deleted_at")
        )
        db_session.add(author)
        await db_session.commit()
        return author

    return create


@pytest_asyncio.fixture
async def create_author(author_factory):
    """Удобная фикстура для создания одного автора"""

    async def _create(name=None, description=None, **kwargs):
        return await author_factory(
            name=name,
            description=description,
            **kwargs
        )

    return _create


@pytest_asyncio.fixture
async def create_authors(author_factory, fake):
    """Удобная фикстура для создания нескольких авторов"""

    async def _create(count = 3):
        authors = []
        for _ in range(count):
            author = await author_factory()
            authors.append(author)
        return authors

    return _create