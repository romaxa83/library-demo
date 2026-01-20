import uvicorn
import os
import signal
import httpx

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, status, Depends
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from src.core.dependencies.rate_limit import rate_limiter_factory
from src.core.dependencies.redis import get_redis
from src.core.schemas.responses import ErrorBaseResponse
from src.config import config
from src.database import init_db, dispose
from src.logger import init_logger
from src.core.errors.errors_handlers import register_errors_handlers
from src.core.middlewares.middlewares import register_middlewares
from src.core.middlewares.requests_count import requests_count_middleware_dispatch
from src.faststream.broker import broker
from src.setup import (
    setup_static_dirs,
    register_all_routers,
    setup_app_mounts,
    setup_monitoring
)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # --- STARTUP ---
    # Инициализируем БД с конфигом реальной БД
    init_db(config.db.url)
    init_logger()

    setup_static_dirs()

    redis = get_redis()

    FastAPICache.init(
        RedisBackend(redis),
        prefix=config.cache.prefix,
    )

    # FastStream (RabbitMQ)
    await broker.start()

    yield
    # --- SHUTDOWN ---

    await dispose()
    await broker.stop() # FastStream (RabbitMQ)
    await redis.aclose()


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

setup_monitoring(app)
register_errors_handlers(app)
register_middlewares(app)
register_all_routers(app)
setup_app_mounts(app)

rate_limit_info = rate_limiter_factory("info", 5, 5)
rate_limit_health = rate_limiter_factory("info", 3, 10)


async def check_worker_via_api() -> bool:
    # URL для получения информации об очередях
    # rabbitmq — это имя сервиса в docker-compose
    url = f"http://{config.rabbitmq.host}:15672/api/queues/%2f/user-registered"

    auth = (config.rabbitmq.user, config.rabbitmq.password)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, auth=auth, timeout=2.0)
            if response.status_code == 200:
                data = response.json()
                # consumers — количество активных обработчиков на этой очереди
                return data.get("consumers", 0) > 0
            return False
    except Exception:
        return False

@app.get("/", dependencies=[Depends(rate_limit_info)])
async def info():
    try:
        broker_ok = await broker.ping(timeout=5.0)
        redis = get_redis()
        redis_ok = await redis.ping()
        worker_online = await check_worker_via_api()

        return {
            "app": config.app.name,
            "env": config.app.env,
            "status": "ok",
            "broker_ping": broker_ok,
            "redis_ping": redis_ok,
            "worker_online": worker_online
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

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

@app.get("/health", dependencies=[Depends(rate_limit_health)])
async def health_check():
    try:
        broker_ok = await broker.ping(timeout=5.0)
        redis = get_redis()
        redis_ok = await redis.ping()

        return {
            "status": "ok",
            "broker_ping": broker_ok,
            "redis_ping": redis_ok,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.get("/stop")
def stop_server():
    print("Получен запрос на остановку сервера. Завершаем...")
    os.kill(os.getpid(), signal.SIGTERM)

if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
