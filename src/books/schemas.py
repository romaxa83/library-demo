from datetime import datetime
from pydantic import BaseModel, ConfigDict


# ==================== Author ====================
class AuthorBase(BaseModel):
    name: str


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorBase):
    pass


class AuthorResponse(AuthorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ==================== Category ====================
class CategoryBase(BaseModel):
    title: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

# ==================== Book ====================
class BookBase(BaseModel):
    title: str
    description: str | None = None
    page: int = 0
    is_available: bool = True
    author_id: int
    category_id: int


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    page: int | None = None
    is_available: bool | None = None
    author_id: int | None = None
    category_id: int | None = None


class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

class BookDetailResponse(BookResponse):
    """Книга с вложенными объектами автора и категории"""
    author: AuthorResponse
    category: CategoryResponse