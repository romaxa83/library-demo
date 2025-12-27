import pytest
from faker import Faker
from src.rbac.models import Role

@pytest.fixture
def fake():
    return Faker()

@pytest.fixture
def role_factory(db_session, fake):
    def create(**kwargs):
        model = Role(
            alias=kwargs.get("alias") or fake.sentence(nb_words=5),
        )
        db_session.add(model)
        db_session.commit()
        return model

    return create


@pytest.fixture
def create_role(role_factory):
    def _create(**kwargs):
        return role_factory(**kwargs)

    return _create


@pytest.fixture
def create_roles(role_factory):
    def _create(count=3):
        models = []
        for _ in range(count):
            model = role_factory()
            models.append(model)
        return models

    return _create