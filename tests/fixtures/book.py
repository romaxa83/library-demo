import pytest_asyncio
from faker import Faker
from src.books.models import Book

@pytest_asyncio.fixture
def fake():
    """Фикстура для генерации фейковых данных"""
    return Faker()


@pytest_asyncio.fixture
async def book_factory(db_session, fake, author_factory):
    """Фабрика для создания тестовых книг"""

    async def create(**kwargs):
        # Создаём автора, если не передан
        author = kwargs.get("author") or await author_factory()

        book = Book(
            title=kwargs.get("title") or fake.sentence(nb_words=3),
            description=kwargs.get("description") or fake.text(max_nb_chars=300),
            page=kwargs.get("page") or fake.random_int(min=100, max=500),
            is_available=kwargs.get("is_available", True),
            author_id=author.id,
            deleted_at=kwargs.get("deleted_at")
        )
        db_session.add(book)
        await db_session.commit()
        return book

    return create


@pytest_asyncio.fixture
async def create_book(book_factory):
    """Удобная фикстура для создания одной книги"""

    async def _create(title=None, author=None, **kwargs):
        return await book_factory(title=title, author=author, **kwargs)

    return _create


@pytest_asyncio.fixture
async def create_books(book_factory):
    """Удобная фикстура для создания нескольких книг"""

    async def _create(count=3, author=None):
        books = []
        for _ in range(count):
            book = await book_factory(author=author)
            books.append(book)
        return books

    return _create