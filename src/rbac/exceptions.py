from fastapi import HTTPException, status

class ForbiddenError(HTTPException):
    def __init__(self, detail: str = 'Forbidden'):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class RoleNotFoundError(HTTPException):
    def __init__(self, role_id: int):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with id [{role_id}] not found")

class RoleCanNotDeleteError(HTTPException):
    def __init__(self, detail: str = 'Role can not be deleted'):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class RoleNotFoundByAliasError(HTTPException):
    def __init__(self, alias: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with alias [{alias}] not found")

class PermissionNotFoundError(HTTPException):
    def __init__(self, permission_id: int):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Permission with id [{permission_id}] not found")