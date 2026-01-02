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


app = FastAPI()

register_errors_handlers(app)

app.include_router(auth_router)
app.include_router(rbac_router)
app.include_router(books_router)

config = Config()

# Инициализируем БД с конфигом реальной БД
init_db(config.db.url)
# Инициализируем БД с конфигом реальной БД
init_logger()

@app.get("/")
def info():
    return {"app": config.app.name, "env": config.app.env, "version": "1.0"}

@app.get("/stop")
def stop_server():
    print("Получен запрос на остановку сервера. Завершаем...")
    os.kill(os.getpid(), signal.SIGKILL)

if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
