from typing import Sequence

from fastapi_cache import FastAPICache
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from loguru import logger
from src.users.models import User

from src.rbac.permissions import (
    DefaultRole,
    get_permissions_for_seed,
    get_permissions_for_roles
)
from src.rbac.exceptions import (
    RoleNotFoundError,
    PermissionNotFoundError,
    RoleNotFoundByAliasError,
    RoleCanNotDeleteError
)
from src.rbac.schemas import (
    RoleCreate,
    RoleUpdate,
    PermissionCreate,
    PermissionUpdate,
    PermissionsDetailResponse,
)
from src.rbac.models import Role, Permission
import  asyncio


class RbacService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_roles(self, exclude_aliases: list[str] | None = None) -> Sequence[Role]:

        stmt = (select(Role)
                .options(selectinload(Role.permissions)))

        if exclude_aliases:
            stmt = stmt.where(Role.alias.not_in(exclude_aliases))


        return (await self.session.scalars(stmt)).all()

    async def get_by_id(self, role_id: int) -> Role:
        """Получить роль по ID"""
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        model = await self.session.scalar(stmt)

        if not model:
            raise RoleNotFoundError(role_id)

        return model

    async def get_permission_by_id(self, permission_id: int) -> Permission:
        stmt = (
            select(Permission)
            .where(Permission.id == permission_id)
        )
        model = await self.session.scalar(stmt)

        if not model:
            raise PermissionNotFoundError(permission_id)

        return model

    async def find_role_by_alias(self, alias: str) -> Role|None:
        """Получить роль по алиасу"""
        stmt = (select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.alias == alias))
        model = await self.session.scalar(stmt)

        return model

    async def get_role_by_alias(self, alias: str) -> Role|None:
        """Получить роль по алиасу"""
        stmt = (select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.alias == alias))
        model = await self.session.scalar(stmt)

        if not model:
            raise RoleNotFoundByAliasError(alias)

        return model

    async def find_permission_by_alias(self, alias: str) -> Permission|None:
        stmt = (select(Permission).where(Permission.alias == alias))
        model = await self.session.scalar(stmt)

        return model

    async def create_role(self, data: RoleCreate) -> Role:

        perms = []
        if data.permission_ids:
            stmt = select(Permission).where(Permission.id.in_(data.permission_ids))
            perms = (await self.session.scalars(stmt)).all()

        data_role = data.model_dump(exclude={"permission_ids"})
        model = Role(**data_role)

        if perms:
            model.permissions = list(perms)

        self.session.add(model)

        await self.session.commit()

        logger.success(f"Created role: {model.alias}")

        return await self.get_by_id(model.id)

    async def update_role(self, role_id: int, data: RoleUpdate) -> Role:
        """Обновить роль"""
        model = await self.get_by_id(role_id)

        data_update_role = data.model_dump(exclude={"permission_ids"})

        for field, value in data_update_role.items():
            setattr(model, field, value)
        await self.session.flush()

        if data.permission_ids:
            model.permissions.clear()
            for perm_id in data.permission_ids:
                perm = await self.get_permission_by_id(perm_id)
                model.permissions.append(perm)

        await self.session.commit()

        return await self.get_by_id(model.id)

    async def delete_role(self, role_id: int) -> None:
        """Удаляем роль"""
        stmt = select(Role).where(Role.id == role_id)
        model = await self.session.scalar(stmt)

        if not model or model.is_superadmin:
            raise RoleNotFoundError(role_id)

        if model.is_default:
            raise RoleCanNotDeleteError

        user_exists_stmt = select(exists().where(User.role_id == role_id))
        has_users = await self.session.scalar(user_exists_stmt)
        if has_users:
            raise RoleCanNotDeleteError(detail="Cannot delete role because it is assigned to one or more users")

        await self.session.delete(model)
        await self.session.commit()

    async def get_all_permissions(self) -> Sequence[PermissionsDetailResponse]:

        stmt = select(Permission)

        permissions = (await self.session.scalars(stmt)).all()

        return [PermissionsDetailResponse.model_validate(p) for p in permissions]

    async def create_permission(self, data: PermissionCreate) -> Permission:
        model = Permission(**data.model_dump())

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        return model

    async def update_permission(self, permission_id: int, data: PermissionUpdate) -> Permission:
        model = await self.get_permission_by_id(permission_id)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(model, field, value)

        await self.session.commit()
        await self.session.refresh(model)

        return model

    async def insert_default_roles(self) -> None:
        for role in DefaultRole:
            if await self.find_role_by_alias(alias=role.value) is None:
                # asyncio.run(
                    await self.create_role(RoleCreate(alias=role.value))
                # )

    async def attach_permissions_to_role(self) -> None:
        for role_alias, perms in get_permissions_for_roles().items():
            if role := await self.get_role_by_alias(alias=role_alias):
                role.permissions.clear()
                for perm_alias in perms:
                    if perm := await self.find_permission_by_alias(alias=perm_alias):
                        role.permissions.append(perm)

                await self.session.commit()

    async def insert_or_update_permission(self) -> None:
        # FastAPICache.clear(namespace=config.cache.namespace.permissions)

        for group, perms in get_permissions_for_seed().items():
            for perm in perms:
                if model := await self.find_permission_by_alias(alias=perm['alias']):
                    # asyncio.run(
                        await self.update_permission(
                            permission_id=model.id,
                            data=PermissionUpdate(description=perm['description'])
                        # )
                    )
                else:
                    # asyncio.run(
                        await self.create_permission(
                            PermissionCreate(
                                group=group,
                                alias=perm['alias'],
                                description=perm['description'],
                            )
                        )
                    # )