import asyncio
import typer
from datetime import datetime
from sqlalchemy import select

from src.config import config, BASE_DIR
from src.database import init_db, dispose
from src.rbac.service import RbacService
from src.books.service import BookService
from src.users.models import User
from src.auth import utils as auth_utils
from src.rbac.models import Role
from src.rbac.permissions import DefaultRole
from src.rbac.exceptions import RoleNotFoundByAliasError

seed_app = typer.Typer()


def coro(f):
    """Декоратор для запуска асинхронных функций в синхронном Typer"""
    import functools
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    functools.update_wrapper(wrapper, f)
    return wrapper


@seed_app.command()
@coro
async def perms():
    """Запуск сидера дефолтных ролей и разрешений, запуск - python -m cli.main seed perms"""
    init_db()
    from src.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        service = RbacService(db)
        try:
            await service.insert_or_update_permission()
            print("✅ Загружены пермишины")
            await service.insert_default_roles()
            print("✅ Загружены роли")
            await service.attach_permissions_to_role()
            print("✅ Привязаны пермишины к роли")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        finally:
            await dispose()


@seed_app.command()
@coro
async def superadmin():
    """Создание супер-администратора, python -m cli.main seed superadmin"""
    init_db()
    from src.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            # Находим роль
            stmt_role = select(Role).where(Role.alias == DefaultRole.SUPERADMIN.value)
            role = await db.scalar(stmt_role)

            if not role:
                raise RoleNotFoundByAliasError(DefaultRole.SUPERADMIN.value)

            # Проверяем существование пользователя
            stmt_user = select(User).where(User.email == config.app.superadmin_email)
            user = await db.scalar(stmt_user)

            if user:
                print("⚠️ Superadmin already exists")
                return

            # Создаем модель
            model = User(
                email=config.app.superadmin_email,
                password=auth_utils.hash_password(config.app.superadmin_password),
                username="superadmin",
                # Используем наивную дату для соответствия asyncpg (как обсуждали ранее)
                email_verify_at=datetime.now(),
                role_id=role.id
            )

            db.add(model)
            await db.commit()

            print(f"✅ Создан супер-админ - (email:{config.app.superadmin_email}, password:{config.app.superadmin_password})")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
        finally:
            await dispose()

@seed_app.command()
@coro
async def books():
    """Запуск сидера для загрузки тестовых данных, запуск - python -m cli.main seed books"""
    init_db()
    from src.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        path = BASE_DIR / "storage" / "book_data.json"
        service = BookService(db)
        try:
            await service.import_json_to_db(path)
            print("✅ Загружены книги")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        finally:
            await dispose()