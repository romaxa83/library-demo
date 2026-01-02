from pydantic import BaseModel, Field
from typing import Generic, Tuple, TypeVar

T = TypeVar("T")  # Generic тип для моделей

class MsgResponse(BaseModel):
    msg: str | None = None

class SuccessResponse(MsgResponse):
    success: bool = True

class ErrorResponse(MsgResponse):
    success: bool = False

class ResponseList(BaseModel, Generic[T]):
    data: list[T] = Field(description="Данные")