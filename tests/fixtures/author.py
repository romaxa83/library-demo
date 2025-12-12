import pytest
from faker import Faker

from src.books.models import Author


@pytest.fixture
def fake():
    """Фикстура для генерации фейковых данных"""
    return Faker()


@pytest.fixture
def author_factory(db_session, fake):
    """Фабрика для создания тестовых авторов"""

    def create(**kwargs):
        author = Author(
            name=kwargs.get("name") or fake.name(),
            description=kwargs.get("description") or fake.text(max_nb_chars=200),
            deleted_at=kwargs.get("deleted_at")
        )
        db_session.add(author)
        db_session.commit()
        return author

    return create


@pytest.fixture
def create_author(author_factory):
    """Удобная фикстура для создания одного автора"""

    def _create(name=None, description=None, **kwargs):
        return author_factory(
            name=name,
            description=description,
            **kwargs
        )

    return _create


@pytest.fixture
def create_authors(author_factory, fake):
    """Удобная фикстура для создания нескольких авторов"""

    def _create(count = 3):
        authors = []
        for _ in range(count):
            author = author_factory()
            authors.append(author)
        return authors

    return _create