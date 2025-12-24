from fastapi import APIRouter, Query, status

from src.books.dependencies import BookServiceDep
from src.books.schemas import (
    AuthorCreate,
    AuthorDetailResponse,
    AuthorFilterSchema,
    AuthorShortResponse,
    AuthorUpdate,
    BookCreate,
    BookDetailResponse,
    BookResponse,
    BookUpdate,
    BookFilterSchema
)
from src.utils.pagination import PaginatedResponse, PaginationHelper

# router = APIRouter(
#     prefix="/books",
#     tags=["Books"]
# )

router = APIRouter()


# ==================== AUTHORS ====================
@router.get(
    "/authors",
    summary="Получить список авторов",
    tags=["Authors"],
    response_model=PaginatedResponse[AuthorShortResponse],
)
async def get_authors(
    service: BookServiceDep,
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    search: str | None = Query(None, description="Поиск по имени автора"),
    deleted: str = Query("active", description="Фильтр по статусу удаления (active, deleted, all)"),
    sort_by: str = Query("name", description="Поле для сортировки (name)"),
    sort_order: str = Query("asc", description="Порядок сортировки (asc, desc)"),
):
    filters = AuthorFilterSchema(
        skip=skip,
        limit=limit,
        search=search,
        deleted=deleted,
        sort_by=sort_by,
        sort_order=sort_order
    )

    authors, total = service.get_all_authors(filters=filters)

    return PaginationHelper.build_paginated_response(data=authors, total=total, skip=skip, limit=limit)


@router.get(
    "/authors/{author_id}", summary="Получить автора по ID", tags=["Authors"],
)
async def get_author(author_id: int, service: BookServiceDep):
    """Получить автора по ID"""
    return service.get_author_by_id(author_id)


@router.post(
    "/authors",
    response_model=AuthorDetailResponse,
    summary="Создать нового автора",
    tags=["Authors"],
    status_code=status.HTTP_201_CREATED,
)
async def create_authors(data: AuthorCreate, service: BookServiceDep):
    """Создать новую книгу"""
    return service.create_author(data)


@router.patch("/authors/{author_id}", summary="Обновить автора", tags=["Authors"], response_model=AuthorDetailResponse)
async def update_authors(author_id: int, data: AuthorUpdate, service: BookServiceDep):
    """Обновить книгу"""
    return service.update_author(author_id, data)


@router.delete(
    "/authors/{author_id}",
    summary="Удалить автора (soft delete)",
    tags=["Authors"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_author(author_id: int, service: BookServiceDep):
    """Удалить автора (soft delete)"""
    service.delete_author(author_id)


@router.patch(
    "/authors/{author_id}/restore",
    tags=["Authors"],
    summary="Восстановить удалённого автора",
    response_model=AuthorDetailResponse,
)
async def restore_author(author_id: int, service: BookServiceDep):
    """Восстановить удалённого автора"""
    return service.restore_author(author_id)


@router.delete(
    "/authors/{author_id}/force",
    tags=["Authors"],
    summary="Полностью удалить автора из БД",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def force_delete_author(author_id: int, service: BookServiceDep):
    """
    Полностью удалить автора из БД.
    Можно использовать только для уже удалённых авторов (soft-deleted).
    """
    service.force_delete_author(author_id)


# ===============================================
# ==================== BOOKS ====================
# ===============================================


@router.get(
    "/books",
    tags=["Books"],
    summary="Получить список всех книг",
    response_model=PaginatedResponse[BookDetailResponse],
)
async def get_books(
    service: BookServiceDep,
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    search: str | None = Query(None, description="Поиск по названию"),
    author_id: int | None = Query(0, description="Поиск по автору"),
    is_available: bool | None = Query(None, description="Поиск книги по наличию"),
    deleted: str = Query("active", description="Фильтр по статусу удаления (active, deleted, all)"),
    sort_by: str = Query("name", description="Поле для сортировки (title, page, is_available, created_at)"),
    sort_order: str = Query("asc", description="Порядок сортировки (asc, desc)"),):
    """Получить список всех книг"""

    filters = BookFilterSchema(
        skip=skip,
        limit=limit,
        search=search,
        author_id=author_id,
        is_available=is_available,
        deleted=deleted,
        sort_by=sort_by,
        sort_order=sort_order
    )

    recs, total = service.get_all_books(filters=filters)

    return PaginationHelper.build_paginated_response(data=recs, total=total, skip=skip, limit=limit)


@router.get(
    "/books/{book_id}",
    tags=["Books"],
    summary="Получить книгу по ID",
    response_model=BookDetailResponse
)
async def get_book(book_id: int, service: BookServiceDep):
    """Получить книгу по ID"""
    return service.get_by_id(book_id)


@router.post(
    "/books",
    tags=["Books"],
    response_model=BookResponse,
    summary="Создать новую книгу",
    status_code=status.HTTP_201_CREATED,
)
async def create_book(data: BookCreate, service: BookServiceDep):
    """Создать новую книгу"""
    return service.create(data)


@router.patch("/books/{book_id}", tags=["Books"], summary="Обновить книгу", response_model=BookResponse)
async def update_book(book_id: int, data: BookUpdate, service: BookServiceDep):
    """Обновить книгу"""
    return service.update(book_id, data)


@router.delete("/books/{book_id}", tags=["Books"], summary="Удалить книгу", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, service: BookServiceDep):
    """Удалить книгу"""
    service.delete(book_id)
