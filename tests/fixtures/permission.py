import pytest_asyncio
from faker import Faker
from src.rbac.models import Permission

@pytest_asyncio.fixture
def fake():
    return Faker()

@pytest_asyncio.fixture
async def permission_factory(db_session, fake):
    async def create(**kwargs):
        model = Permission(
            alias=kwargs.get("alias") or fake.sentence(nb_words=3),
            group=kwargs.get("group") or fake.sentence(nb_words=3),
            description=kwargs.get("description") or fake.text(max_nb_chars=50),
        )
        db_session.add(model)
        await db_session.commit()
        await db_session.refresh(model)
        return model

    return create


@pytest_asyncio.fixture
async def create_permission(permission_factory):
    async def _create(**kwargs):
        return await permission_factory(**kwargs)

    return _create


@pytest_asyncio.fixture
async def create_permissions(permission_factory):
    async def _create(count=3):
        models = []
        for _ in range(count):
            model = await permission_factory()
            models.append(model)
        return models

    return _create