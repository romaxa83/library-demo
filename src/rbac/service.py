from typing import Sequence

from fastapi_cache import FastAPICache
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from loguru import logger

from src.config import config
from src.rbac.permissions import (
    DefaultRole,
    get_permissions_for_seed,
    get_permissions_for_roles
)
from src.rbac.exceptions import (
    RoleNotFoundError,
    PermissionNotFoundError,
    RoleNotFoundByAliasError
)
from src.rbac.schemas import (
    RoleCreate,
    RoleUpdate,
    PermissionCreate,
    PermissionUpdate, PermissionsDetailResponse,
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
        stmt = (select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.alias == alias))
        model = self.session.scalar(stmt)

        return model

    def get_role_by_alias(self, alias: str) -> Role|None:
        """Получить роль по алиасу"""
        stmt = (select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.alias == alias))
        model = self.session.scalar(stmt)

        if not model:
            raise RoleNotFoundByAliasError(alias)

        return model

    def find_permission_by_alias(self, alias: str) -> Permission|None:
        stmt = (select(Permission).where(Permission.alias == alias))
        model = self.session.scalar(stmt)

        return model

    async def create_role(self, data: RoleCreate) -> Role:
        data_role = data.model_dump(exclude={"permission_ids"})

        model = Role(**data_role)

        self.session.add(model)
        self.session.flush()

        if data.permission_ids:
            for perm_id in data.permission_ids:
                perm = self.get_permission_by_id(perm_id)
                model.permissions.append(perm)

        self.session.commit()
        self.session.refresh(model)

        logger.success(f"Created role: {model.alias}")

        return model

    def update_role(self, role_id: int, data: RoleUpdate) -> Role:
        """Обновить роль"""
        model = self.get_by_id(role_id)

        data_update_role = data.model_dump(exclude={"permission_ids"})

        for field, value in data_update_role.items():
            setattr(model, field, value)
        self.session.flush()

        if data.permission_ids:
            model.permissions.clear()
            for perm_id in data.permission_ids:
                perm = self.get_permission_by_id(perm_id)
                model.permissions.append(perm)

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

    def get_all_permissions(self) -> Sequence[PermissionsDetailResponse]:

        stmt = select(Permission)

        permissions = self.session.scalars(stmt).all()

        return [PermissionsDetailResponse.model_validate(p) for p in permissions]

    async def create_permission(self, data: PermissionCreate) -> Permission:
        model = Permission(**data.model_dump())

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        # logger.success(f"Created permission: {model.alias}")

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

    def attach_permissions_to_role(self) -> None:
        for role_alias, perms in get_permissions_for_roles().items():
            if role := self.get_role_by_alias(alias=role_alias):
                role.permissions.clear()
                for perm_alias in perms:
                    if perm := self.find_permission_by_alias(alias=perm_alias):
                        role.permissions.append(perm)

                self.session.commit()

    def insert_or_update_permission(self) -> None:
        # FastAPICache.clear(namespace=config.cache.namespace.permissions)

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