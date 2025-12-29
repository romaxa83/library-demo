from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from loguru import logger

from src.rbac.permissions import (
    DefaultRole,
    get_permissions_for_seed
)
from src.rbac.exceptions import (
    RoleNotFoundError,
    PermissionNotFoundError,
)
from src.rbac.schemas import (
    RoleCreate,
    RoleUpdate,
    PermissionCreate,
    PermissionUpdate,
)
from src.rbac.models import Role, Permission
import  asyncio


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

    def get_permission_by_id(self, permission_id: int) -> Permission:
        stmt = (
            select(Permission)
            .where(Permission.id == permission_id)
        )
        model = self.session.scalar(stmt)

        if not model:
            raise PermissionNotFoundError(permission_id)

        return model

    def find_role_by_alias(self, alias: str) -> Role|None:
        """Получить роль по алиасу"""

        stmt = (select(Role).
                options(selectinload(Role.permissions))
                .where(Role.alias == alias))
        model = self.session.scalar(stmt)

        return model

    def find_permission_by_alias(self, alias: str) -> Permission|None:
        stmt = (select(Permission).where(Permission.alias == alias))
        model = self.session.scalar(stmt)

        return model

    async def create_role(self, data: RoleCreate) -> Role:
        model = Role(**data.model_dump())

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        logger.success(f"Created role: {model.alias}")

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

    async def create_permission(self, data: PermissionCreate) -> Permission:
        model = Permission(**data.model_dump())

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        logger.success(f"Created permission: {model.alias}")

        return model

    async def update_permission(self, permission_id: int, data: PermissionUpdate) -> Permission:
        model = self.get_permission_by_id(permission_id)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(model, field, value)

        self.session.commit()
        self.session.refresh(model)

        return model

    def insert_default_roles(self) -> None:
        for role in DefaultRole:
            if self.find_role_by_alias(alias=role.value) is None:
                asyncio.run(self.create_role(RoleCreate(alias=role.value)))

    def insert_or_update_permission(self) -> None:
        for group, perms in get_permissions_for_seed().items():
            for perm in perms:
                if model := self.find_permission_by_alias(alias=perm['alias']):
                    asyncio.run(
                        self.update_permission(
                            permission_id=model.id,
                            data=PermissionUpdate(description=perm['description'])
                        )
                    )
                else:
                    asyncio.run(
                        self.create_permission(
                            PermissionCreate(
                                group=group,
                                alias=perm['alias'],
                                description=perm['description'],
                            )
                        )
                    )