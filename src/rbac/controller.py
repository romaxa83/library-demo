from typing import Annotated, Any, Callable, Dict, Optional, Tuple
from fastapi import APIRouter, status, Depends, Request, Response
from fastapi_cache.decorator import cache
import hashlib
from src.rbac.dependencies import PermissionRequired
from src.rbac.permissions import Permissions, DefaultRole

from src.rbac.exceptions import (
    RoleNotFoundError
)
from src.core.schemas.responses import ResponseList
from src.rbac.dependencies import RbacServiceDep
from src.rbac.schemas import (
    RoleDetailResponse,
    RoleCreate,
    RoleUpdate,
    PermissionsDetailResponse
)
from src.rbac.models import Role
from src.rbac.service import RbacService
from src.users.models import User
from src.config import config

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
    data = await service.get_all_roles(
        exclude_aliases=[DefaultRole.SUPERADMIN.value]
    )

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

    model = await service.get_by_id(role_id)
    if model.is_superadmin:
        raise RoleNotFoundError(role_id)

    return model

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
    return await service.update_role(role_id, data)

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
    return await service.delete_role(role_id)

def perm_list_key_builder(
    func: Callable[..., Any],
    namespace: str,
    *,
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
) -> str:

    # убираем обьекты из kwards так как они постоянно имеют другой адрес из-за чего ключ для кеша всегда разные
    exclude_types = (RbacService,User)
    # exclude_types = ()
    cache_kw = {}
    for name, value in kwargs.items():
        if isinstance(value, exclude_types):
            continue
        cache_kw[name] = value

    cache_key = hashlib.md5(  # noqa: S324
        f"{func.__module__}:{func.__name__}:{args}:{cache_kw}".encode()
    ).hexdigest()
    return f"{namespace}:{cache_key}"

@router.get(
    "/permissions",
    summary="Список разрешений",
    response_model=ResponseList[PermissionsDetailResponse]
)
# todo нужно доработать чтоб кеш не срабатывал при тестах
# @cache(
#     expire=60*10,
#     key_builder=perm_list_key_builder,
#     namespace=config.cache.namespace.permissions,
# )
async def get_permissions(
    service: RbacServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.PERMISSION_LIST))]
)->ResponseList[PermissionsDetailResponse]:
    data = await service.get_all_permissions()
    return ResponseList(data=data)
