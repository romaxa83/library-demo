from pydantic import BaseModel, Field
from typing import Generic, Tuple, TypeVar

T = TypeVar("T")  # Generic тип для моделей

class SuccessResponse(BaseModel):
    msg: str | None = None
    success: bool = True

class ResponseList(BaseModel, Generic[T]):
    data: list[T] = Field(description="Данные")