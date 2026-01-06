from typing import Annotated, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from fastapi import Depends

from src.config import Config

config = Config()

# Не создаём engine здесь, это будет сделано в функции ниже
engine = None
SessionLocal = None

class Base(DeclarativeBase):
    pass

def init_db(db_url: str = None):
    """Инициализация БД с использованием конкретного URL"""
    global engine, SessionLocal

    if db_url is None:
        db_url = config.db.url

    engine = create_engine(
        db_url,
        echo=False, # вывод логов в терминал
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine, SessionLocal

def get_db():
    """Получить сессию БД"""
    if SessionLocal is None:
        init_db()

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DbSessionDep = Annotated[Session, Depends(get_db)]