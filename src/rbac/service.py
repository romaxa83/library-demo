from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.rbac.exceptions import RoleNotFoundError
from src.rbac.schemas import (
    RoleCreate,
    RoleUpdate,
)
from src.rbac.models import Role, Permission


class RbacService:
    def __init__(self, session: Session):
        self.session = session

    def get_all_roles(self) -> Sequence[Role]:

        stmt = select(Role)

        return self.session.scalars(stmt).all()

    def get_by_id(self, role_id: int) -> Role:
        """Получить роль по ID"""
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        model = self.session.scalar(stmt)

        if not model:
            raise RoleNotFoundError(role_id)

        return model

    async def create_role(self, data: RoleCreate) -> Role:
        model = Role(**data.model_dump())

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        return model

    def update_role(self, role_id: int, data: RoleUpdate) -> Role:
        """Обновить роль"""
        model = self.get_by_id(role_id)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(model, field, value)

        self.session.commit()
        self.session.refresh(model)
        return model

    def delete_role(self, role_id: int) -> None:
        """Удаляем роль"""
        stmt = select(Role).where(Role.id == role_id)
        model = self.session.scalar(stmt)

        # todo добавить проверку что нельзя удалить роль которая привязана к пользователю, а также дефолтный роли (установленные в системе)
        if not model:
            raise RoleNotFoundError(role_id)

        self.session.delete(model)
        self.session.commit()

    def get_all_permissions(self) -> Sequence[Permission]:

        stmt = select(Permission)

        return self.session.scalars(stmt).all()