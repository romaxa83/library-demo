import pytest
from faker import Faker
from datetime import datetime, timezone
from src.users.models import User
from src.auth import utils as auth_utils
from sqlalchemy import select

@pytest.fixture
def fake():
    """Фикстура для генерации фейковых данных"""
    return Faker()


@pytest.fixture
def user_factory(db_session, fake):
    """Фабрика для создания тестовых книг"""

    def create(**kwargs):
        model = User(
            username=kwargs.get("username") or fake.user_name(),
            email=kwargs.get("email") or fake.email(),
            email_verify_at=kwargs.get("email_verify_at"),
            password=kwargs.get("password",) or fake.password(),
            is_active=kwargs.get("is_active", True),
            deleted_at=kwargs.get("deleted_at"),
            created_at=kwargs.get("created_at") or datetime.now(tz=timezone.utc),
            updated_at=kwargs.get("updated_at") or datetime.now(tz=timezone.utc)
        )

        model.password = auth_utils.hash_password(model.password)

        db_session.add(model)
        db_session.commit()

        print("FIXTURE")
        # print(model)

        # print(db_session.scalars(select(User)).all())

        return model

    return create


@pytest.fixture
def create_user(user_factory):
    """Удобная фикстура для создания одного пользователя"""

    def _create(username=None, **kwargs):
        return user_factory(username=username, **kwargs)

    return _create


@pytest.fixture
def create_users(user_factory):
    """Удобная фикстура для создания нескольких пользователей"""

    def _create(count=3):
        models = []
        for _ in range(count):
            model = user_factory()
            models.append(model)
        return models

    return _create