from typing import Annotated
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

from src.books.service import BookService
from src.database import DbSessionDep

def get_book_service(session: DbSessionDep) -> BookService:
    """Получить сервис книг"""
    return BookService(session)

# Type alias для удобства
BookServiceDep = Annotated[BookService, Depends(get_book_service)]