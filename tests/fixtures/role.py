import pytest_asyncio
from faker import Faker
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.rbac.models import Role, Permission

@pytest_asyncio.fixture
def fake():
    return Faker()

@pytest_asyncio.fixture
async def role_factory(db_session, fake):
    async def create(permissions: list[str] = None, **kwargs):
        """
        Фабрика для создания ролей.

        Args:
            permissions: Список алиасов разрешений ["author.list", "author.create"]
            **kwargs: Поля для модели Role (например, alias)
        """
        model = Role(
            alias=kwargs.get("alias") or fake.sentence(nb_words=5),
        )

        if permissions:
            # Загружаем объекты разрешений из базы
            stmt = select(Permission).where(Permission.alias.in_(permissions))
            perm_objects = (await db_session.scalars(stmt)).all()
            # Привязываем их к роли
            model.permissions = list(perm_objects)

        db_session.add(model)

        await db_session.commit()
        # Перезагружаем объект со связями
        stmt_refresh = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == model.id)
        )
        return await db_session.scalar(stmt_refresh)

    return create


@pytest_asyncio.fixture
async def create_role(role_factory):
    async def _create(permissions: list[str] = None, **kwargs):
        return await role_factory(permissions=permissions, **kwargs)

    return _create


@pytest_asyncio.fixture
async def create_roles(role_factory):
    async def _create(count=3, permissions: list[str] = None):
        models = []
        for _ in range(count):
            model = await role_factory(permissions=permissions)
            models.append(model)
        return models

    return _create