from typing import Annotated
from fastapi import APIRouter, status, Depends

from src.rbac.dependencies import PermissionRequired
from src.rbac.permissions import Permissions

from src.core.schemas.responses import ResponseList
from src.rbac.dependencies import RbacServiceDep
from src.rbac.schemas import (
    RoleDetailResponse,
    RoleCreate,
    RoleUpdate,
    PermissionsDetailResponse
)
from src.rbac.models import Role
from src.users.models import User

router = APIRouter(
    tags=["RBAC"]
)

@router.get(
    "/roles",
    summary="Список ролей",
    response_model=ResponseList[RoleDetailResponse],
)
async def get_roles(
    service: RbacServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.ROLE_LIST))]
)->ResponseList[RoleDetailResponse]:
    data = service.get_all_roles()

    return ResponseList(data=data)

@router.get(
    "/roles/{role_id}",
    response_model=RoleDetailResponse,
    summary="Получить роль по ID",
)
async def get_role(
    role_id: int,
    service: RbacServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.ROLE_SHOW))]
)->Role:
    return service.get_by_id(role_id)

@router.post(
    "/roles",
    response_model=RoleDetailResponse,
    summary="Создать новую роль",
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    data: RoleCreate,
    service: RbacServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.ROLE_CREATE))]
)->Role:
    return await service.create_role(data)

@router.patch(
    "/roles/{role_id}",
    summary="Обновить роль",
    response_model=RoleDetailResponse
)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    service: RbacServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.ROLE_UPDATE))]
):
    return service.update_role(role_id, data)

@router.delete(
    "/roles/{role_id}",
    summary="Удалить роль",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_role(
    role_id: int,
    service: RbacServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.ROLE_DELETE))]
)->None:
    return service.delete_role(role_id)

@router.get(
    "/permissions",
    summary="Список разрешений",
    response_model=ResponseList[PermissionsDetailResponse]
)
async def get_permissions(
    service: RbacServiceDep,
user: Annotated[User, Depends(PermissionRequired(Permissions.PERMISSION_LIST))]
):
    data = service.get_all_permissions()
    return ResponseList(data=data)
