from fastapi import APIRouter, status

from src.core.schemas.responses import ResponseList
from src.rbac.dependencies import RbacServiceDep
from src.rbac.schemas import (
    RoleDetailResponse,
    RoleCreate,
    RoleUpdate,
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
async def get_role(role_id: int, service: RbacServiceDep):
    pass

@router.post(
    "/roles",
    response_model=RoleDetailResponse,
    summary="Создать новую роль",
    status_code=status.HTTP_201_CREATED,
)
async def create_role(data: RoleCreate, service: RbacServiceDep):
    pass

@router.patch(
    "/roles/{role_id}",
    summary="Обновить роль",
    response_model=RoleDetailResponse
)
async def update_role(
    author_id: int,
    data: RoleUpdate,
    service: RbacServiceDep
):
    pass

@router.delete(
    "/roles/{role_id}",
    summary="Удалить роль",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_role(role_id: int, service: RbacServiceDep):
    pass

@router.get(
    "/permissions",
    summary="Список разрешений",
)
async def get_permissions(service: RbacServiceDep):
    pass
