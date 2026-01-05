import typer
from datetime import datetime, timezone
from src.config import Config
from src.database import init_db
from src.rbac.service import RbacService
from src.users.models import User
from src.auth import utils as auth_utils
from sqlalchemy import select
from src.rbac.models import Role
from src.rbac.permissions import DefaultRole
from src.rbac.exceptions import RoleNotFoundByAliasError

seed_app = typer.Typer()
config = Config()

def run_seed_roles_permissions():
    init_db()
    # Теперь SessionLocal больше не None, это фабрика сессий
    from src.database import SessionLocal

    with SessionLocal() as db:
        service = RbacService(db)
        try:
            service.insert_or_update_permission()
            print("✅ Загружены пермишины")
            service.insert_default_roles()
            print("✅ Загружены роли")
            service.attach_permissions_to_role()
            print("✅ Привязаны пермишины к роли")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

@seed_app.command()
def perms():
    """Запуск сидера дефолтных ролей, разрешений и их связей: python -m cli.main seed perms"""
    run_seed_roles_permissions()

def create_super_admin():
    # print(config.app)
    init_db()
    # Теперь SessionLocal больше не None, это фабрика сессий
    from src.database import SessionLocal

    with SessionLocal() as db:
        try:

            stmt = (select(Role)
                    .where(Role.alias == DefaultRole.SUPERADMIN.value))
            role = db.scalar(stmt)

            if not role:
                raise RoleNotFoundByAliasError(DefaultRole.SUPERADMIN.value)

            query = select(User).where(User.email == config.app.superadmin_email)
            user = db.scalar(query)
            if user:
                raise Exception("Superadmin already exists")

            model = User(
                email=config.app.superadmin_email,
                password=auth_utils.hash_password(config.app.superadmin_password),
                username="superadmin",
                email_verify_at=datetime.now(timezone.utc),
                role_id=role.id
            )

            db.add(model)
            db.commit()

            print("✅ Создан супер-админ")

        except Exception as e:
            print(f"❌ Ошибка: {e}")

@seed_app.command()
def superadmin():
    """Запуск сидера дефолтных ролей, разрешений и их связей: python -m cli.main seed superadmin"""
    create_super_admin()

