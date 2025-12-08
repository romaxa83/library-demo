from fastapi import FastAPI
import uvicorn
from src.books.router import router as books_router

import importlib

# Импорт модуля
# import math_utils

from src.config import Config

app = FastAPI()

app.include_router(books_router)

config = Config()

# importlib.reload(math_utils)

@app.get("/")
def info():
    return {
        "app": config.app.name,
        "env": config.app.env,
        "version": "1.0"
    }

if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)