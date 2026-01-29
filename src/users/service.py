from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from src.rbac.models import Role
from src.users.exceptions import UserNotFoundError
from src.users.models import User


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_email(self, email: str) -> User:
        stmt = select(User).where(User.email == email)
        model = await self.session.scalar(stmt)

        if not model or model.deleted_at is not None:
            raise UserNotFoundError()

        return model

    async def find_by_email(self, email: str|EmailStr) -> User | None:
        stmt = select(User).where(User.email == email)
        model = await self.session.scalar(stmt)

        return model

    async def find_by_id(self, id: str|int) -> User | None:
        stmt = (select(User)
                .options(
                    joinedload(User.role).joinedload(Role.permissions)
                )
                .where(User.id == id))
        model = await self.session.scalar(stmt)

        return model

    async def get_by_id(self, id: str|int) -> User:
        stmt = (
            select(User)
            .options(
                joinedload(User.role)
                .joinedload(Role.permissions)
            )
            .where(User.id == id))
        model = await self.session.scalar(stmt)

        if not model or model.deleted_at is not None:
            raise UserNotFoundError()

        return model
