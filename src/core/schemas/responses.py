from pydantic import BaseModel

class SuccessResponse(BaseModel):
    msg: str | None = None
    success: bool = True