from typing import Annotated, Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from src.rbac.service import RbacService
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


def get_service(session: Annotated[Session, Depends(get_session)]) -> RbacService:
    return RbacService(session)

RbacServiceDep = Annotated[RbacService, Depends(get_service)]