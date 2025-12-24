from pydantic import BaseModel, ConfigDict

class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, strict=True)

    token_type: str
    access_token: str
