from faststream.rabbit import RabbitRouter
from loguru import logger
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from faststream import Depends as BrokerDepends

from src.auth import utils as auth_utils
from src.database import get_db
from src.notifications.send_email import send_verification_email
from src.users.models import User

router = RabbitRouter()

@router.subscriber("user-registered")
async def user_registered(
    user_id: int,
    session: Annotated[AsyncSession, BrokerDepends(get_db)]
)->None:
    """
    Обработчик регистрации пользователя:
     - Отправка mail для подтверждения email
     - запись в логи

    :param user_id: User id
    :return: None
    """

    logger.info(f"User registered - [{user_id}]")

    stmt = select(User).where(User.id == user_id)
    user = await session.scalar(stmt)
    logger.info(f"User registered - [{user.email}]")

    verify_token = auth_utils.create_verify_email_token({
        "sub": str(user.id),
        "email": user.email,
    })

    await send_verification_email(user, verify_token)