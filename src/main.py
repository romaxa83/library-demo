import uvicorn
from fastapi import FastAPI

from src.books.router import router as books_router
from src.config import Config

app = FastAPI()

app.include_router(books_router)

config = Config()


@app.get("/")
def info():

    print(config.db.url)
    return {"app": config.app.name, "env": config.app.env, "version": "1.0"}


if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
