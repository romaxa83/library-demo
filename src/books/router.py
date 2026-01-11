from typing import Annotated
from fastapi import APIRouter, Query, status, Depends, UploadFile, File, HTTPException

from src.media.schemas import ImageUploadValidation
from src.rbac.dependencies import PermissionRequired
from src.rbac.permissions import Permissions
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
from src.books.models import Book, Author
from src.users.models import User
from src.utils.pagination import PaginatedResponse, PaginationHelper

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
    user: Annotated[User, Depends(PermissionRequired(Permissions.AUTHOR_LIST))],
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    search: str | None = Query(None, description="Поиск по имени автора"),
    deleted: str = Query("active", description="Фильтр по статусу удаления (active, deleted, all)"),
    sort_by: str = Query("name", description="Поле для сортировки (name)"),
    sort_order: str = Query("asc", description="Порядок сортировки (asc, desc)"),
)->list[Author]:
    filters = AuthorFilterSchema(
        skip=skip,
        limit=limit,
        search=search,
        deleted=deleted,
        sort_by=sort_by,
        sort_order=sort_order
    )

    authors, total = await service.get_all_authors(filters=filters)

    return PaginationHelper.build_paginated_response(data=authors, total=total, skip=skip, limit=limit)


@router.get(
    "/authors/{author_id}",
    summary="Получить автора по ID",
    tags=["Authors"],
    response_model=AuthorDetailResponse
)
async def get_author(
    author_id: int,
    service: BookServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.AUTHOR_SHOW))]
)->Author:
    """Получить автора по ID"""
    return await service.get_author_by_id(author_id)


@router.post(
    "/authors",
    response_model=AuthorDetailResponse,
    summary="Создать нового автора",
    tags=["Authors"],
    status_code=status.HTTP_201_CREATED,
)
async def create_authors(
    data: AuthorCreate,
    service: BookServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.AUTHOR_CREATE))]
)->Author:
    """Создать новую книгу"""
    return await service.create_author(data)


@router.patch("/authors/{author_id}", summary="Обновить автора", tags=["Authors"], response_model=AuthorDetailResponse)
async def update_authors(
    author_id: int,
    data: AuthorUpdate,
    service: BookServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.AUTHOR_UPDATE))]
)->Author:
    """Обновить книгу"""
    return await service.update_author(author_id, data)


@router.delete(
    "/authors/{author_id}",
    summary="Удалить автора (soft delete)",
    tags=["Authors"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_author(
    author_id: int,
    service: BookServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.AUTHOR_DELETE))]
)->None:
    """Удалить автора (soft delete)"""
    await service.delete_author(author_id)


@router.patch(
    "/authors/{author_id}/restore",
    tags=["Authors"],
    summary="Восстановить удалённого автора",
    response_model=AuthorDetailResponse,
)
async def restore_author(
    author_id: int,
    service: BookServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.AUTHOR_RESTORE))]
)->Author:
    """Восстановить удалённого автора"""
    return await service.restore_author(author_id)


@router.delete(
    "/authors/{author_id}/force",
    tags=["Authors"],
    summary="Полностью удалить автора из БД",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def force_delete_author(
    author_id: int,
    service: BookServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.AUTHOR_FORCE_DELETE))]
)->None:
    """
    Полностью удалить автора из БД.
    Можно использовать только для уже удалённых авторов (soft-deleted).
    """
    await service.force_delete_author(author_id)


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
    user: Annotated[User, Depends(PermissionRequired(Permissions.BOOK_LIST))],
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

    recs, total = await service.get_all_books(filters=filters)

    return PaginationHelper.build_paginated_response(data=recs, total=total, skip=skip, limit=limit)


@router.get(
    "/books/{book_id}",
    tags=["Books"],
    summary="Получить книгу по ID",
    response_model=BookDetailResponse
)
async def get_book(
    book_id: int,
    service: BookServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.BOOK_SHOW))]
)->Book:
    """Получить книгу по ID"""
    return await service.get_by_id(book_id)


@router.post(
    "/books",
    tags=["Books"],
    response_model=BookResponse,
    summary="Создать новую книгу",
    status_code=status.HTTP_201_CREATED,
)
async def create_book(
    data: BookCreate,
    service: BookServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.BOOK_CREATE))]
)->Book:
    """Создать новую книгу"""
    return await service.create(data)


@router.patch(
    "/books/{book_id}",
    tags=["Books"],
    summary="Обновить книгу",
    response_model=BookResponse
)
async def update_book(
    book_id: int,
    data: BookUpdate,
    service: BookServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.BOOK_UPDATE))]
)->Book:
    """Обновить книгу"""
    return await service.update(book_id, data)


@router.delete("/books/{book_id}", tags=["Books"], summary="Удалить книгу", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    service: BookServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.BOOK_DELETE))]
)->None:
    """Удалить книгу"""
    await service.delete(book_id)

@router.post(
    "/books/{book_id}/upload-img",
    tags=["Books"],
    summary="Загрузить картинки для книги",
    status_code=status.HTTP_200_OK,
    response_model=BookDetailResponse
)
async def upload_img_for_book(
    book_id: int,
    file: Annotated[UploadFile, File(description="Файл для загрузки")],
    service: BookServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.BOOK_UPLOAD_IMG))]
)->Book:
    """Загрузить картинки для книги"""

    try:
        # В FastAPI seek() асинхронный, но принимает только 1 аргумент (offset)
        # Чтобы узнать размер, мы читаем файл до конца
        content = await file.read()
        file_size = len(content)

        # ВАЖНО: После чтения курсор в конце файла. Нужно вернуть его в начало,
        # чтобы сервис мог прочитать файл заново.
        await file.seek(0)

        ImageUploadValidation.validate(file.content_type, file_size)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return await service.upload_img(book_id, file)
