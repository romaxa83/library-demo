import typer
import asyncio
from src.database import init_db
from src.rbac.service import RbacService


seed_app = typer.Typer()

def run_seed_roles_permissions():
    init_db()

    # Теперь SessionLocal больше не None, это фабрика сессий
    from src.database import SessionLocal

    with SessionLocal() as db:
        # 3. Инициализируем сервис, передавая сессию
        service = RbacService(db)

        try:
            service.insert_or_update_permission()
            print("✅ Пользователь успешно создан")
        except Exception as e:
            print(f"❌ Ошибка: {e}")


@seed_app.command()
def perms():
    """Запуск сидера дефолтных ролей, разрешений и их связей: python -m cli.main seed perms"""
    run_seed_roles_permissions()

