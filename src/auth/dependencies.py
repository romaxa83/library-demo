from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import InvalidTokenError

from src.auth.exceptions import UnauthorizedError
from src.auth.service import AuthService
from src.database import DbSessionDep
from src.users.models import User


http_bearer = HTTPBearer()

def get_auth_service(session: DbSessionDep) -> AuthService:
    """Получить сервис auth"""
    return AuthService(session)

# Type alias для удобства
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

def get_current_user(
    service: AuthServiceDep,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> User:
    token = credentials.credentials
    try:
        return service.current_user(token)
    except InvalidTokenError as err:
        raise UnauthorizedError(detail=str(err))

CurrentUserDep = Annotated[User, Depends(get_current_user)]
