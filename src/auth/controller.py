from fastapi import APIRouter, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import InvalidTokenError
from loguru import logger

from src.auth.dependencies import AuthServiceDep
from src.auth.exceptions import UnauthorizedError
from src.users.schemas import (
    UserRegister,
    UserLogin,
    UserDetailResponse
)
from src.auth.schemas import (
    TokenResponse,
    ForgotPassword,
    ResetPassword,
)
from src.core.schemas.responses import (
    SuccessResponse,
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
async def signup(data: UserRegister, service: AuthServiceDep) -> UserDetailResponse:
    """Регистрация нового пользователя"""

    # print(data)
    # logger.info(data)

    return await service.register(data)

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

@router.post(
    "/refresh-tokens",
    summary="Обновление токенов",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse
)
def refresh_tokens(
    service: AuthServiceDep,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> TokenResponse:
    """Обновление токенов"""
    token = credentials.credentials

    return service.refresh_tokens(token)

@router.get(
    "/verify-email",
    summary="Верификация почты по токену",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse
)
async def verify_email(
    service: AuthServiceDep,
    token: str,
) -> SuccessResponse:
    """Верификация почты"""
    return await service.verify_email(token)

@router.post(
    "/forgot-password",
    summary="Запрос на обновление пароля",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse
)
async def forgot_password(data: ForgotPassword, service: AuthServiceDep,
) -> SuccessResponse:
    """Запрос на обновление пароля"""

    return await service.forgot_password(data)

@router.post(
    "/reset-password",
    summary="Обновление пароля",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse
)
async def reset_password(
    data: ResetPassword,
    service: AuthServiceDep,
) -> SuccessResponse:
    """Обновление пароля"""

    return await service.reset_password(data)