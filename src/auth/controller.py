from fastapi import APIRouter, Query, status

from loguru import logger
from src.auth.dependencies import AuthServiceDep
from src.users.schemas import (
    UserRegister
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post(
    "/signup",
    summary="Регистрация пользователя",
    status_code=status.HTTP_201_CREATED,
)
def create_authors(data: UserRegister, service: AuthServiceDep):
    """Регистрация нового пользователя"""

    # logger.info(data)

    return service.register(data)
