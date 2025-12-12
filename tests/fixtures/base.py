import pytest
from faker import Faker


@pytest.fixture(scope="session")
def fake():
    """Фикстура для генерации фейковых данных"""
    return Faker()