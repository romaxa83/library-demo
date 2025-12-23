from pydantic import BaseModel, Field, EmailStr, ConfigDict

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, strict=True)

    username: str = Field(min_length=1)
    email: EmailStr
    password: bytes
    ia_active: bool

class UserRegister(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(min_length=1)
    email: EmailStr
    password: str

