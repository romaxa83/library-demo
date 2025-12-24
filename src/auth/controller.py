from fastapi import APIRouter, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import InvalidTokenError
from loguru import logger
from src.auth import utils as auth_utils
from src.auth.dependencies import AuthServiceDep
from src.auth.exceptions import UnauthorizedError
from src.users.schemas import (
    UserRegister,
    UserLogin,
    UserDetailResponse
)
from src.auth.schemas import (
    TokenResponse,
)

http_bearer = HTTPBearer()

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post(
    "/signup",
    summary="Регистрация пользователя",
    status_code=status.HTTP_201_CREATED,
    response_model=UserDetailResponse
)
def signup(data: UserRegister, service: AuthServiceDep):
    """Регистрация нового пользователя"""

    # logger.info(data)

    return service.register(data)

@router.post(
    "/login",
    summary="Авторизация пользователя",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse
)
def login(data: UserLogin, service: AuthServiceDep) -> TokenResponse:
    """Авторизация пользователя"""
    return service.login(data)


@router.get(
    "/current-user",
    summary="Получение текущего авторизованного пользователя",
    status_code=status.HTTP_200_OK,
    response_model=UserDetailResponse
)
def current_user(
        service: AuthServiceDep,
        credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> UserDetailResponse:
    """Получение текущего авторизованного пользователя"""
    token = credentials.credentials

    try:
        return service.current_user(token)
    except InvalidTokenError as err:
        raise UnauthorizedError(detail=str(err))