import uvicorn
from fastapi import FastAPI

from src.books.router import router as books_router
from src.config import Config
from src.database import init_db

app = FastAPI()

app.include_router(books_router)

config = Config()

# Инициализируем БД с конфигом реальной БД
init_db(config.db.url)

@app.get("/")
def info():

    print(config.db.url)
    return {"app": config.app.name, "env": config.app.env, "version": "1.0"}


if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
