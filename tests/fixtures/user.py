import pytest_asyncio
from faker import Faker
from datetime import datetime, timezone

from sqlalchemy.orm import joinedload, selectinload

from src.auth.service import AuthService
from src.rbac.models import Role
from src.rbac.permissions import DefaultRole
from src.users.models import User
from src.auth import utils as auth_utils
from sqlalchemy import select

@pytest_asyncio.fixture
def fake():
    """Фикстура для генерации фейковых данных"""
    return Faker()

async def _load_user_with_role(db_session, user_id: int) -> User:
    """Загрузить пользователя с ролью и пермишенами"""
    stmt = (
        select(User)
        .options(
            joinedload(User.role).selectinload(Role.permissions)
        )
        .where(User.id == user_id)
    )
    return await db_session.scalar(stmt)

async def _create_access_token(db_session, user: User) -> str:
    """Создает токен для пользователя"""
    auth_service = AuthService(db_session)
    return auth_service._create_access_token(user)

@pytest_asyncio.fixture
async def user_factory(db_session, fake, create_role, create_permission):
    """Фабрика для создания тестовых пользователей с ролью"""

    async def create(
        username: str = None,
        email: str = None,
        password: str = None,
        role_alias: str = DefaultRole.USER.value,
        permissions: dict | list = None,
        is_active: bool = True,
        email_verify_at: datetime = None,
        **kwargs
    ):
        """
        Создает пользователя с ролью и пермишенами.

        Args:
            username: Имя пользователя
            email: Email пользователя
            password: Пароль (будет захеширован)
            role_alias: Алиас роли (по умолчанию "user")
            permissions: Словарь пермишенов вида {
                "alias": "author.list",
                "group": "author",  # опционально
                "description": "List authors"  # опционально
            } или список алиасов ["author.list", "author.show"]
            is_active: Активен ли пользователь
            email_verify_at: Время верификации email
            **kwargs: Дополнительные поля

            Returns:
                User: Созданный пользователь с загруженной ролью и пермишенами
            """

        stmt_role = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.alias == role_alias)
        )
        role = await db_session.scalar(stmt_role)

        # Получаем или создаем роль через фикстуру
        if not role:
            role = await create_role(alias=role_alias)
            await db_session.refresh(role, ["permissions"])

        # Обрабатываем пермишены
        if permissions:
            if isinstance(permissions, list):
                # Если это список алиасов
                for perm_alias in permissions:
                    # Извлекаем группу из алиаса (например, "author.list" -> "author")
                    group = perm_alias.split(".")[0] if "." in perm_alias else "general"
                    perm = await create_permission(alias=perm_alias, group=group)
                    if perm not in role.permissions:
                        role.permissions.append(perm)
            elif isinstance(permissions, dict):
                # Если это один пермишен как словарь
                perm = await create_permission(
                    alias=permissions.get("alias"),
                    group=permissions.get("group") or permissions.get("alias").split(".")[0],
                    description=permissions.get("description")
                )
                if perm not in role.permissions:
                    role.permissions.append(perm)

            await db_session.commit()

        model = User(
            username=username or fake.user_name(),
            email=email or fake.email(),
            password=auth_utils.hash_password(password or fake.password()),
            email_verify_at=email_verify_at,
            is_active=is_active,
            role_id=role.id,
            deleted_at=kwargs.get("deleted_at"),
            created_at=kwargs.get("created_at") or datetime.now(),
            updated_at=kwargs.get("updated_at") or datetime.now(),
        )

        db_session.add(model)
        await db_session.commit()

        # Загружаем пользователя с ролью и пермишенами
        return await _load_user_with_role(db_session, model.id)

    return create


@pytest_asyncio.fixture
async def create_user(user_factory):
    """Удобная фикстура для создания одного пользователя"""

    async def _create(
        username: str = None,
        email: str = None,
        password: str = None,
        role_alias: str = DefaultRole.USER.value,
        permissions: dict | list = None,
        **kwargs
    ):
        """
        Создает пользователя.

        Примеры использования:
            # Пользователь с ролью "user" и без доп. прав
            user = create_user()

            # Пользователь с дополнительными пермишенами
            user = create_user(permissions=["author.list", "author.show"])

            # Пользователь с пермишеном как словарь
            user = create_user(permissions={
                "alias": "author.list",
                "group": "author",
                "description": "Custom desc"
            })

            # Пользователь с кастомной ролью
            user = create_user(role_alias="admin", permissions=["author.create"])
        """
        return await user_factory(
            username=username,
            email=email,
            password=password,
            role_alias=role_alias,
            permissions=permissions,
            **kwargs
        )

    return _create


@pytest_asyncio.fixture
async def create_users(user_factory):
    """Удобная фикстура для создания нескольких пользователей"""

    async def _create(
        count: int = 3,
        role_alias: str = DefaultRole.USER.value,
        permissions: dict | list = None,
        **kwargs
    ):
        """
        Создает несколько пользователей с одинаковой ролью и пермишенами.
        """
        users = []
        for _ in range(count):
            user = await user_factory(
                role_alias=role_alias,
                permissions=permissions,
                **kwargs
            )
            users.append(user)
        return users

    return _create

@pytest_asyncio.fixture
async def superadmin_user(user_factory):
    """Создает супер-администратора"""
    return await user_factory(role_alias=DefaultRole.SUPERADMIN.value)

@pytest_asyncio.fixture
async def auth_access_token(db_session, user)->str:
    """Генерирует JWT токен для авторизованного пользователя"""
    auth_service = AuthService(db_session)
    return auth_service._create_access_token(user)


@pytest_asyncio.fixture
async def auth_header(db_session):
    """Создает заголовки авторизации для любого пользователя"""

    async def _create(user: User) -> dict:
        token = await _create_access_token(db_session, user)
        return {"Authorization": f"Bearer {token}"}

    return _create

@pytest_asyncio.fixture
async def superadmin_token(db_session, superadmin_user) -> str:
    """Генерирует JWT токен для супер-администратора"""
    return await _create_access_token(db_session, superadmin_user)

@pytest_asyncio.fixture
async def superadmin_headers(superadmin_token):
    """Возвращает заголовки с токеном супер-администратора"""
    return {"Authorization": f"Bearer {superadmin_token}"}