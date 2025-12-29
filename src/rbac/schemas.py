from pydantic import BaseModel, ConfigDict, Field

class RoleBase(BaseModel):
    alias: str = Field(min_length=1)

class PermissionsBase(BaseModel):
    alias: str = Field(min_length=1)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

class RoleDetailResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    permissions: list[PermissionsBase]

class PermissionsDetailResponse(PermissionsBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    group: str = Field(min_length=1)
    description: str | None = None