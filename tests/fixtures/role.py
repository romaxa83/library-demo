import pytest_asyncio
from faker import Faker
from src.rbac.models import Role

@pytest_asyncio.fixture
def fake():
    return Faker()

@pytest_asyncio.fixture
async def role_factory(db_session, fake):
    async def create(**kwargs):
        model = Role(
            alias=kwargs.get("alias") or fake.sentence(nb_words=5),
        )
        db_session.add(model)
        await db_session.commit()
        await db_session.refresh(model)
        return model

    return create


@pytest_asyncio.fixture
async def create_role(role_factory):
    async def _create(**kwargs):
        return await role_factory(**kwargs)

    return _create


@pytest_asyncio.fixture
async def create_roles(role_factory):
    async def _create(count=3):
        models = []
        for _ in range(count):
            model = await role_factory()
            models.append(model)
        return models

    return _create