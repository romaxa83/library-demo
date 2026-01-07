import uvicorn
from fastapi import FastAPI
import os
import signal
from src.books.router import router as books_router
from src.auth.controller import router as auth_router
from src.rbac.controller import router as rbac_router
from src.config import Config
from src.database import init_db
from src.logger import init_logger
from src.core.errors.errors_handlers import register_errors_handlers
from src.core.middlewares.middlewares import register_middlewares
from src.core.middlewares.requests_count import requests_count_middleware_dispatch

config = Config()

# Инициализируем БД с конфигом реальной БД
init_db(config.db.url)

app = FastAPI(
    title=config.app.name,
)

init_logger()

register_errors_handlers(app)
register_middlewares(app)

app.include_router(auth_router)
app.include_router(rbac_router)
app.include_router(books_router)

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
