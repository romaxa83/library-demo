from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.auth import utils as auth_utils
from src.users.dependencies import UserServiceDep
from src.users.models import User
from src.users.schemas import (
    UserRegister,
    UserLogin,
)
from src.auth.schemas import (
    TokenResponse,
)
from src.auth.utils import (
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
)
from src.auth.exceptions import UnauthorizedError
from loguru import logger

http_bearer = HTTPBearer()

class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.user_service = UserServiceDep

    def register(self, data: UserRegister) -> User:
        """Зарегистрировать нового пользователя"""

        model = User(**data.model_dump())

        model.password = auth_utils.hash_password(data.password)

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        return model

    def login(self, data: UserLogin) -> TokenResponse:

        user = self.user_service.find_by_email(self, email=data.email)

        if (
                not user
                or not user.is_active
                or user.deleted_at is not None
                or not auth_utils.check_password(data.password, user.password)
            ):
            raise UnauthorizedError(detail="Invalid credentials")

        payload = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
        }

        return TokenResponse(
            token_type="Bearer",
            access_token=auth_utils.create_access_token(payload),
            refresh_token=auth_utils.create_refresh_token({"sub": str(user.id)}),
        )

    def refresh_tokens(self, token: str) -> TokenResponse:
        payload = auth_utils.decode_jwt(token=token)

        if payload.get(TOKEN_TYPE_FIELD) != REFRESH_TOKEN_TYPE:
            raise UnauthorizedError(detail="Invalid token type")

        user = self.user_service.find_by_id(self, id=int(payload.get("sub")))

        if (
                not user
                or not user.is_active
                or user.deleted_at is not None
            ):
            raise UnauthorizedError(detail="Invalid credentials")

        payload = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
        }

        return TokenResponse(
            token_type="Bearer",
            access_token=auth_utils.create_access_token(payload),
            refresh_token=auth_utils.create_refresh_token({"sub": str(user.id)}),
        )

    def current_user(self, token: str)->User | None :
        payload = auth_utils.decode_jwt(token=token)

        if payload.get(TOKEN_TYPE_FIELD) != ACCESS_TOKEN_TYPE:
            raise UnauthorizedError(detail="Invalid token type")

        user = self.user_service.find_by_id(self, id=int(payload.get("sub")))

        if (
                not user
                or not user.is_active
                or user.deleted_at is not None
            ):
            raise UnauthorizedError(detail="Invalid credentials")

        return self.user_service.find_by_id(self, id=int(payload.get("sub")))
