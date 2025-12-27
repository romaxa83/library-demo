import pytest
from faker import Faker
from src.rbac.models import Permission

@pytest.fixture
def fake():
    return Faker()

@pytest.fixture
def permission_factory(db_session, fake):
    def create(**kwargs):
        model = Permission(
            alias=kwargs.get("alias") or fake.sentence(nb_words=3),
            group=kwargs.get("group") or fake.sentence(nb_words=3),
            description=kwargs.get("description") or fake.text(max_nb_chars=50),
        )
        db_session.add(model)
        db_session.commit()
        return model

    return create


@pytest.fixture
def create_permission(permission_factory):
    def _create(**kwargs):
        return permission_factory(**kwargs)

    return _create


@pytest.fixture
def create_permissions(permission_factory):
    def _create(count=3):
        models = []
        for _ in range(count):
            model = permission_factory()
            models.append(model)
        return models

    return _create