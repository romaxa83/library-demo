from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.books.service import BookService
from src.database import SessionLocal

# Здесь должна быть ваша настройка базы данных


def get_session() -> Generator[Session, None, None]:
    """Получить сессию базы данных"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_book_service(session: Annotated[Session, Depends(get_session)]) -> BookService:
    """Получить сервис книг"""
    return BookService(session)


# Type alias для удобства
BookServiceDep = Annotated[BookService, Depends(get_book_service)]
