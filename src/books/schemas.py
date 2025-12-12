from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# ==================== Author ====================
class AuthorBase(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorBase):
    pass


class AuthorShortResponse(AuthorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str | None = None  # Исключаем из ответа


class AuthorDetailResponse(AuthorBase):
    """Полная информация об авторе"""

    model_config = ConfigDict(from_attributes=True)

    id: int


# Фильтры ====================
class DeletedStatus(str, Enum):
    """Статус удаления"""

    ACTIVE = "active"  # только не удалённые
    DELETED = "deleted"  # только удалённые
    ALL = "all"  # все


class AuthorFilterSchema(BaseModel):
    """Фильтры для авторов"""

    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
    search: str | None = Field(None, description="Поиск по имени")
    deleted: str = Field("active", description="Статус удаления")
    sort_by: str = Field("name", description="Поле для сортировки (name, created_at)")
    sort_order: str = Field("asc", description="Порядок сортировки (asc, desc)")


# ==================== Book ====================
class BookBase(BaseModel):
    title: str
    description: str | None = None
    page: int = 0
    is_available: bool = True
    author_id: int


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    page: int | None = None
    is_available: bool | None = None
    author_id: int | None = None


class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class BookDetailResponse(BookResponse):
    """Книга с вложенными объектами автора"""

    author: AuthorDetailResponse
