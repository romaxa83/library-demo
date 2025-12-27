from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, strict=True)

    username: str = Field(min_length=1)
    email: EmailStr
    password: bytes

class UserRegister(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(min_length=1)
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str

class UserDetailResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    email_verify_at: datetime | None
    password: bytes = Field(exclude=True)

