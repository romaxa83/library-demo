from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.security import HTTPBearer

from src.core.schemas.responses import SuccessResponse
from src.notifications.send_email import (
    send_verification_email,
    send_email_verified,
    send_email_forgot_password,
    send_email_reset_password
)
from src.auth import utils as auth_utils
from src.users.dependencies import UserServiceDep
from src.users.models import User
from datetime import datetime, timezone
from src.users.schemas import (
    UserRegister,
    UserLogin,
)
from src.auth.schemas import (
    TokenResponse,
    ForgotPassword,
    ResetPassword
)
from src.auth.utils import (
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    VERIFY_EMAIL_TOKEN_TYPE,
    RESET_PASSWORD_TOKEN_TYPE,
)
from src.auth.exceptions import UnauthorizedError
from src.users.exceptions import UserNotFoundError
from loguru import logger

http_bearer = HTTPBearer()

class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.user_service = UserServiceDep

    async def register(self, data: UserRegister) -> User:
        """Зарегистрировать нового пользователя"""

        model = User(**data.model_dump())

        # print(self.session, model)

        model.password = auth_utils.hash_password(data.password)

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        verify_token = auth_utils.create_verify_email_token({
            "sub": str(model.id),
            "email": model.email,
        })

        await send_verification_email(model, verify_token)

        return model

    def login(self, data: UserLogin) -> TokenResponse:
        # user = self.user_service.find_by_email(self, email=data.email)



        q = select(User).where(User.email == data.email)
        user = self.session.scalar(q)

        print("++++++++++++++++++++++++++++++")
        print(data.email)
        print(user)

        s = select(User)
        count = self.session.scalars(s).all()
        print(count)
        # print(select(User).)
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

    async def verify_email(self, token: str)-> SuccessResponse:
        payload = auth_utils.decode_jwt(token=token)

        if payload.get(TOKEN_TYPE_FIELD) != VERIFY_EMAIL_TOKEN_TYPE:
            return SuccessResponse(msg="Invalid token type")
            # raise UnauthorizedError(detail="Invalid token type")

        model = self.user_service.find_by_id(self, id=int(payload.get("sub")))

        if (
                not model
                or not model.is_active
                or model.deleted_at is not None
        ):
            raise UserNotFoundError()


        if model.email_verify_at:
            return SuccessResponse(msg="The email has already been verified.", success=False)
        print(model)

        model.email_verify_at = datetime.now(timezone.utc)

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        await send_email_verified(model)

        logger.success(f"Verified email for {model.email}")
        return SuccessResponse(msg=f"Verified email for {model.email}")

    async def forgot_password(self, data: ForgotPassword)-> SuccessResponse:

        model = self.user_service.find_by_email(self, email=data.email)

        if (
                not model
                or not model.is_active
                or model.deleted_at is not None
        ):
            raise UserNotFoundError()

        reset_password_token = auth_utils.create_reset_password_token({
            "sub": str(model.id),
            "email": model.email,
        })

        await send_email_forgot_password(model, reset_password_token)

        logger.info(f"Reset password by - {model.email}")
        return SuccessResponse(msg=f"Password reset email sent to {model.email}")

    async def reset_password(self, data: ResetPassword)-> SuccessResponse:

        payload = auth_utils.decode_jwt(token=data.token)

        if payload.get(TOKEN_TYPE_FIELD) != RESET_PASSWORD_TOKEN_TYPE:
            return SuccessResponse(msg="Invalid token type")

        model = self.user_service.find_by_email(self, email=payload.get("email"))

        if (
                not model
                or not model.is_active
                or model.deleted_at is not None
        ):
            raise UserNotFoundError()

        model.password = auth_utils.hash_password(data.password)

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        await send_email_reset_password(model, data.password)

        logger.info(f"Password reset successfully by - {model.email}")
        return SuccessResponse(msg="Password reset successfully")