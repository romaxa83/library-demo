from typing import Annotated, Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from src.books.service import BookService


# Здесь должна быть ваша настройка базы данных
# Пример с SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./library.db"  # или из конфига

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Generator[Session, None, None]:
    """Получить сессию базы данных"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_book_service(
    session: Annotated[Session, Depends(get_session)]
) -> BookService:
    """Получить сервис книг"""
    return BookService(session)


# Type alias для удобства
BookServiceDep = Annotated[BookService, Depends(get_book_service)]