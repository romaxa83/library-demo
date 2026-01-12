from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, status
import os
import signal

from fastapi.staticfiles import StaticFiles
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis

from src.books.router import router as books_router
from src.core.schemas.responses import ErrorBaseResponse
from src.media.router import router as media_router
from src.auth.controller import router as auth_router
from src.rbac.controller import router as rbac_router
from src.config import config
from src.database import init_db, dispose
from src.logger import init_logger
from src.core.errors.errors_handlers import register_errors_handlers
from src.core.middlewares.middlewares import register_middlewares
from src.core.middlewares.requests_count import requests_count_middleware_dispatch


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup
    # Инициализируем БД с конфигом реальной БД
    init_db(config.db.url)
    init_logger()

    redis = Redis(
        host=config.redis.host,
        port=config.redis.port,
        # password=config.redis.password,
        # encoding="utf8",
        # decode_responses=True
    )

    # Проверяем соединение
    await redis.ping()

    FastAPICache.init(
        RedisBackend(redis),
        prefix=config.cache.prefix,
    )

    yield
    # shutdown
    await dispose()
    # await redis.close()


# Общие ответы
COMMON_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorBaseResponse, "description": "Не авторизован (отсутствует или неверный токен)"},
    status.HTTP_403_FORBIDDEN: {"model": ErrorBaseResponse, "description": "Доступ запрещен (недостаточно прав)"},
}

app = FastAPI(
    title=config.app.name,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    responses=COMMON_RESPONSES
)

# Создаем физическую папку в storage
config.media.root_path.mkdir(parents=True, exist_ok=True)
# Создаем папку public
config.media.public_path.mkdir(parents=True, exist_ok=True)

# Монтируем статику.
# ВАЖНО: Если вы используете symlink public/media -> storage/media,
# то FastAPI должен смотреть в public/media.
media_dir = config.media.public_path / "media"

if not media_dir.exists():
    print(f"⚠️  ВНИМАНИЕ: Директория {media_dir} не найдена. Создаю физическую папку вместо ссылки.")
    media_dir.mkdir(parents=True, exist_ok=True)


# Раздаем всё содержимое папки public по корневому пути или через префикс
# Теперь запрос http://app.com/media/book/1.jpg
# пойдет в физическую папку public/media/book/1.jpg
app.mount(
    config.media.url_prefix,
    StaticFiles(directory=config.media.public_path / "media"),
    name="media"
)

register_errors_handlers(app)
register_middlewares(app)


app.include_router(auth_router)
app.include_router(rbac_router)
app.include_router(books_router)
app.include_router(media_router)


@app.get("/")
def info():
    return {
        "app": config.app.name,
        "env": config.app.env,
        "version": "1.0",
        "request_simple_stats": {
            path: {
                "count": stats.count,
                "statuses": dict(stats.statuses_counts),
            }
            for path, stats in requests_count_middleware_dispatch.counts.items()
        }

    }

@app.get("/stop")
def stop_server():
    print("Получен запрос на остановку сервера. Завершаем...")
    os.kill(os.getpid(), signal.SIGKILL)

if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
