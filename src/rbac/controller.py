from fastapi import APIRouter, status

from src.core.schemas.responses import ResponseList
from src.rbac.dependencies import RbacServiceDep
from src.rbac.schemas import (
    RoleDetailResponse,
    RoleCreate,
    RoleUpdate,
    PermissionsDetailResponse
)
from src.rbac.models import (
    Role,
)

router = APIRouter(
    tags=["RBAC"]
)

@router.get(
    "/roles",
    summary="Список ролей",
    response_model=ResponseList[RoleDetailResponse],
)
async def get_roles(service: RbacServiceDep)->ResponseList[RoleDetailResponse]:
    data = service.get_all_roles()

    return ResponseList(data=data)

@router.get(
    "/roles/{role_id}",
    response_model=RoleDetailResponse,
    summary="Получить роль по ID",
)
async def get_role(role_id: int, service: RbacServiceDep)->Role:
    return service.get_by_id(role_id)

@router.post(
    "/roles",
    response_model=RoleDetailResponse,
    summary="Создать новую роль",
    status_code=status.HTTP_201_CREATED,
)
async def create_role(data: RoleCreate, service: RbacServiceDep)->Role:
    return await service.create_role(data)

@router.patch(
    "/roles/{role_id}",
    summary="Обновить роль",
    response_model=RoleDetailResponse
)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    service: RbacServiceDep
):
    return service.update_role(role_id, data)

@router.delete(
    "/roles/{role_id}",
    summary="Удалить роль",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_role(role_id: int, service: RbacServiceDep)->None:
    return service.delete_role(role_id)

@router.get(
    "/permissions",
    summary="Список разрешений",
    response_model=ResponseList[PermissionsDetailResponse]
)
async def get_permissions(service: RbacServiceDep):
    data = service.get_all_permissions()
    return ResponseList(data=data)
