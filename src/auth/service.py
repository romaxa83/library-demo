from sqlalchemy.ext.asyncio import AsyncSession
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
from src.users.service import UserService
from src.users.models import User
from src.rbac.models import Role
from src.rbac.permissions import DefaultRole
from datetime import datetime, timezone
from src.users.schemas import (
    UserRegister,
    UserLogin, UserSimple,
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
from src.rbac.exceptions import RoleNotFoundByAliasError
from src.users.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError
)
from loguru import logger
from src.faststream.broker import broker

http_bearer = HTTPBearer()

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_service = UserService(session)

    async def register(self, data: UserRegister) -> User:
        """Зарегистрировать нового пользователя"""

        role = await self.session.scalar(select(Role).where(Role.alias == DefaultRole.USER.value))
        if not role:
            raise RoleNotFoundByAliasError(DefaultRole.USER.value)

        if await self.session.scalar(select(User).where(User.email == data.email)):
            raise UserAlreadyExistsError(data.email)

        model = User(**data.model_dump())

        model.password = auth_utils.hash_password(data.password)
        model.role_id = role.id

        self.session.add(model)
        await self.session.commit()

        model = await self.user_service.get_by_id(model.id)

        # отправка перенесена в брокер сообщений
        # verify_token = auth_utils.create_verify_email_token({
        #     "sub": str(model.id),
        #     "email": model.email,
        # })
        #
        # await send_verification_email(model, verify_token)

        await broker.publish(
            message=model.id,
            queue="user-registered"
        )


        return model

    async def login(self, data: UserLogin) -> TokenResponse:
        user = await self.user_service.find_by_email(data.email)

        if (
                not user
                or not user.is_active
                or user.deleted_at is not None
                or not auth_utils.check_password(data.password, user.password)
            ):
            raise UnauthorizedError(detail="Invalid credentials")

        return TokenResponse(
            token_type="Bearer",
            access_token=self._create_access_token(user),
            refresh_token=auth_utils.create_refresh_token({"sub": str(user.id)}),
        )

    def _create_access_token(self, user: User)->str:
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
        }

        return auth_utils.create_access_token(payload)

    async def refresh_tokens(self, token: str) -> TokenResponse:
        payload = auth_utils.decode_jwt(token=token)

        if payload.get(TOKEN_TYPE_FIELD) != REFRESH_TOKEN_TYPE:
            raise UnauthorizedError(detail="Invalid token type")

        user = await self.user_service.find_by_id(id=int(payload.get("sub")))

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

    async def current_user(self, token: str)->User | None :
        payload = auth_utils.decode_jwt(token=token)

        if payload.get(TOKEN_TYPE_FIELD) != ACCESS_TOKEN_TYPE:
            raise UnauthorizedError(detail="Invalid token type")

        user = await self.user_service.find_by_id(id=int(payload.get("sub")))

        if (
                not user
                or not user.is_active
                or user.deleted_at is not None
            ):
            raise UnauthorizedError(detail="Invalid credentials")

        return user

    async def verify_email(self, token: str)-> SuccessResponse:
        payload = auth_utils.decode_jwt(token=token)

        if payload.get(TOKEN_TYPE_FIELD) != VERIFY_EMAIL_TOKEN_TYPE:
            return SuccessResponse(msg="Invalid token type")

        model = await self.user_service.find_by_id(self, id=int(payload.get("sub")))

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
        await self.session.commit()
        await self.session.refresh(model)

        await send_email_verified(model)

        logger.success(f"Verified email for {model.email}")
        return SuccessResponse(msg=f"Verified email for {model.email}")

    async def forgot_password(self, data: ForgotPassword)-> SuccessResponse:

        model = await self.user_service.find_by_email(self, email=data.email)

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

        model = await self.user_service.find_by_email(self, email=payload.get("email"))

        if (
                not model
                or not model.is_active
                or model.deleted_at is not None
        ):
            raise UserNotFoundError()

        model.password = auth_utils.hash_password(data.password)

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        await send_email_reset_password(model, data.password)

        logger.info(f"Password reset successfully by - {model.email}")
        return SuccessResponse(msg="Password reset successfully")