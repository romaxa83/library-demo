from fastapi import APIRouter, status

from src.books.dependencies import BookServiceDep
from src.books.schemas import (
    BookCreate,
    BookUpdate,
    BookResponse,
    BookDetailResponse,
    AuthorCreate,
    AuthorUpdate,
    AuthorResponse
)

router = APIRouter(
    prefix="/books",
    tags=["Books"]
)

# ==================== AUTHORS ====================
@router.get(
    "/authors",
    summary="Получить список авторов",
    tags=["Authors"],
    response_model=list[AuthorResponse]
)
async def get_authors(
    service: BookServiceDep,
    skip: int = 0,
    limit: int = 10
):
    """Получить список авторов"""
    return service.get_all_authors(skip=skip, limit=limit)

@router.get(
    "/authors/{author_id}",
    summary="Получить автора по ID",
    tags=["Authors"],
    response_model=AuthorResponse
)
async def get_book(
    author_id: int,
    service: BookServiceDep
):
    """Получить автора по ID"""
    return service.get_author_by_id(author_id)

@router.post(
    "/authors",
    response_model=AuthorResponse,
    summary="Создать нового автора",
    tags=["Authors"],
    status_code=status.HTTP_201_CREATED
)
async def create_authors(
    data: AuthorCreate,
    service: BookServiceDep
):
    """Создать новую книгу"""
    return service.create_author(data)

@router.patch(
    "/authors/{author_id}",
    summary="Обновить автора",
    tags=["Authors"],
    response_model=AuthorResponse
)
async def update_authors(
    author_id: int,
    data: AuthorUpdate,
    service: BookServiceDep
):
    """Обновить книгу"""
    return service.update_author(author_id, data)

@router.delete(
    "/authors/{author_id}",
    summary="Удалить автора",
    tags=["Authors"],
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_author(
    author_id: int,
    service: BookServiceDep
):
    """Удалить автора"""
    service.delete_author(author_id)
# ==================== BOOKS ====================
@router.get(
    "/",
    summary="Получить список всех книг",
    response_model=list[BookDetailResponse]
)
async def get_books(
    service: BookServiceDep,
    skip: int = 0,
    limit: int = 10
):
    """Получить список всех книг"""
    return service.get_all(skip=skip, limit=limit)

@router.get(
    "/{book_id}",
    summary="Получить книгу по ID",
    response_model=BookDetailResponse
)
async def get_book(
    book_id: int,
    service: BookServiceDep
):
    """Получить книгу по ID"""
    return service.get_by_id(book_id)

@router.post(
    "/",
    response_model=BookResponse,
    summary="Создать новую книгу",
    status_code=status.HTTP_201_CREATED
)
async def create_book(
    data: BookCreate,
    service: BookServiceDep
):
    """Создать новую книгу"""
    return service.create(data)

@router.patch(
    "/{book_id}",
    summary="Обновить книгу",
    response_model=BookResponse
)
async def update_book(
    book_id: int,
    data: BookUpdate,
    service: BookServiceDep
):
    """Обновить книгу"""
    return service.update(book_id, data)

@router.delete(
    "/{book_id}",
    summary="Удалить книгу",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_book(
    book_id: int,
    service: BookServiceDep
):
    """Удалить книгу"""
    service.delete(book_id)