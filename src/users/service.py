from sqlalchemy import select
from sqlalchemy.orm import Session

from src.users.exceptions import UserNotFoundError
from src.users.models import User


class UserService:
    def __init__(self, session: Session):
        self.session = session


    def get_by_email(self, email: str) -> User:
        stmt = select(User).where(User.email == email)
        model = self.session.scalar(stmt)

        if not model or model.deleted_at is not None:
            raise UserNotFoundError()

        return model

    def find_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        model = self.session.scalar(stmt)

        return model

    def find_by_id(self, id: str|int) -> User | None:
        stmt = select(User).where(User.id == id)
        model = self.session.scalar(stmt)

        return model
