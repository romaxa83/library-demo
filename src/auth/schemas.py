from pydantic import BaseModel, ConfigDict, EmailStr

class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, strict=True)

    token_type: str
    access_token: str
    refresh_token: str

class ForgotPassword(BaseModel):
    model_config = ConfigDict(from_attributes=True, strict=True)

    email: EmailStr

class ResetPassword(BaseModel):
    model_config = ConfigDict(from_attributes=True, strict=True)

    token: str
    password: str