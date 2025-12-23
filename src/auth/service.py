from sqlalchemy.orm import Session

from src.users.models import User
from src.users.schemas import UserRegister
from loguru import logger

class AuthService:
    def __init__(self, session: Session):
        self.session = session

    def register(self, data: UserRegister) -> User:
        """Зарегистрировать нового пользователя"""

        logger.info(self.session)

        model = User(**data.model_dump())
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model
