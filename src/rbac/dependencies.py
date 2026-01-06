from typing import Annotated
from fastapi import Depends

from src.auth.dependencies import CurrentUserDep
from src.database import DbSessionDep
from src.rbac.exceptions import ForbiddenError
from src.rbac.permissions import Permissions
from src.rbac.service import RbacService

def get_service(session: DbSessionDep) -> RbacService:
    return RbacService(session)

RbacServiceDep = Annotated[RbacService, Depends(get_service)]

class PermissionRequired:
    def __init__(self, permission: Permissions):
        self.permission = permission.value

    def __call__(self, user: CurrentUserDep):
        if not user.has_permission(self.permission):
            raise ForbiddenError(detail=f"Недостаточно прав: требуется {self.permission}")
        return user