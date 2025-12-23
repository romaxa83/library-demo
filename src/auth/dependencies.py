from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.auth.service import AuthService
from src import database


def get_session() -> Generator[Session, None, None]:
    """Получить сессию базы данных"""
    # SessionLocal будет инициализирован в init_db()
    if database.SessionLocal is None:
        database.init_db()

    session = database.SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_auth_service(session: Annotated[Session, Depends(get_session)]) -> AuthService:
    """Получить сервис auth"""
    return AuthService(session)


# Type alias для удобства
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]