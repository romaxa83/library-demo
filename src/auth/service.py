from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.auth import utils as auth_utils
from src.users.dependencies import UserServiceDep
from src.users.models import User
from src.users.schemas import (
    UserRegister,
    UserLogin,
    UserDetailResponse
)
from src.auth.schemas import (
    TokenResponse,
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

        token = auth_utils.encode_jwt(payload)

        return TokenResponse(
            token_type="Bearer",
            access_token=token,
        )

    def current_user(self, token: str):
        payload = auth_utils.decode_jwt(token=token)

        user = self.user_service.find_by_id(self, id=int(payload.get("sub")))

        if (
                not user
                or not user.is_active
                or user.deleted_at is not None
            ):
            raise UnauthorizedError(detail="Invalid credentials")

        return self.user_service.find_by_id(self, id=int(payload.get("sub")))



