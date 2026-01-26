from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from prometheus_fastapi_instrumentator import Instrumentator

from src.config import config
from src.auth.controller import router as auth_router
from src.rbac.controller import router as rbac_router
from src.books.router import router as books_router
from src.media.router import router as media_router

def register_all_routers(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(rbac_router)
    app.include_router(books_router)
    app.include_router(media_router)

def setup_static_dirs():
    """Создание необходимых папок для медиа"""
    # Создаем физическую папку в storage
    config.media.root_path.mkdir(parents=True, exist_ok=True)
    # Создаем папку public
    config.media.public_path.mkdir(parents=True, exist_ok=True)
    # Монтируем статику.
    # ВАЖНО: Если вы используете symlink public/media -> storage/media,
    # то FastAPI должен смотреть в public/media.
    media_dir = config.media.public_path / "media"
    media_dir.mkdir(parents=True, exist_ok=True)

def setup_app_mounts(app: FastAPI):
    """Раздача статики (в режиме разработки)"""
    # В продакшене Nginx сам заберет папку /public
    app.mount(
        config.media.url_prefix,
        StaticFiles(directory=config.media.public_path / "media"),
        name="media"
    )

def setup_monitoring(app: FastAPI):
    """Настройка Prometheus"""
    Instrumentator().instrument(app).expose(app, endpoint='/__internal_metrics__', include_in_schema=False)