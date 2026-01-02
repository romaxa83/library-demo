from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated

class RoleBase(BaseModel):
    alias: str = Field(min_length=1)

class PermissionsBase(BaseModel):
    alias: str = Field(min_length=1)

class RoleCreate(RoleBase):
    permission_ids: list[Annotated[int, Field(gt=0, description="Массив ID permission")]] = []

class RoleUpdate(RoleBase):
    permission_ids: list[Annotated[int, Field(gt=0, description="Массив ID permission")]] = []

class PermissionCreate(RoleBase):
    group: str = Field(min_length=1)
    description: str | None = None

class PermissionUpdate(BaseModel):
    description: str | None = None

class RoleDetailResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    permissions: list[PermissionsBase]

class PermissionsDetailResponse(PermissionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int