from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.users.service import UserService
from src import database


def get_session() -> Generator[Session, None, None]:
    """Получить сессию базы данных"""
    if database.SessionLocal is None:
        database.init_db()

    session = database.SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_user_service(session: Annotated[Session, Depends(get_session)]) -> UserService:
    return UserService(session)


# Type alias для удобства
UserServiceDep = Annotated[UserService, Depends(get_user_service)]