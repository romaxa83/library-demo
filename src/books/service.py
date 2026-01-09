from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from src.books.exceptions import AuthorNotFoundError, BookNotFoundError
from src.books.models import Author, Book
from src.books.schemas import AuthorCreate, AuthorFilterSchema, AuthorUpdate, BookCreate, BookUpdate, BookFilterSchema
from src.utils.pagination import PaginationHelper


class BookService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_books(self, filters: BookFilterSchema) -> tuple[list[Book], int]:
        """
        Получить список книг с фильтрацией и сортировкой

        Args:
            filters: Объект с параметрами фильтрации

        Returns:
            Кортеж (список авторов, всего записей в БД)
        """

        stmt = select(Book).options(selectinload(Book.author).joinedload(Author.books))

        # ✨ Фильтр по статусу удаления
        if filters.deleted == "active":
            stmt = stmt.where(Book.deleted_at.is_(None))
        elif filters.deleted == "deleted":
            stmt = stmt.where(Book.deleted_at.isnot(None))
            # elif filters.deleted == "all" — не добавляем условие, получаем всех

        # ✨ Поиск по имени
        if filters.search:
            stmt = stmt.where(Book.title.ilike(f"%{filters.search}%"))

        # ✨ Поиск по автору
        if filters.author_id:
            stmt = stmt.where(Book.author_id == filters.author_id)

        # ✨ Поиск по наличию
        if filters.is_available == 1:
            stmt = stmt.where(Book.is_available == True)
        elif filters.is_available == 0:
            stmt = stmt.where(Book.is_available == False)

        # ✨ Сортировка
        if filters.sort_by == "page":
            order_column = Book.page
        else:
            order_column = Book.title  # По умолчанию по имени

        if filters.sort_order.lower() == "desc":
            stmt = stmt.order_by(order_column.desc())
        else:
            stmt = stmt.order_by(order_column.asc())

        recs, total = await PaginationHelper.paginate(self.session, stmt, filters.skip, filters.limit)

        return recs, total

    async def get_by_id(self, book_id: int) -> Book:
        """Получить книгу по ID"""
        stmt = (select(Book)
                .options(selectinload(Book.author).joinedload(Author.books))
                .where(Book.id == book_id))
        model = await self.session.scalar(stmt)

        if not model or model.deleted_at is not None:
            raise BookNotFoundError(book_id)

        return model

    async def create(self, data: BookCreate) -> Book:
        """Создать новую книгу"""
        # Проверяем существование автора
        await self._validate_author_exists(data.author_id)

        model = Book(**data.model_dump())
        model.updated_at = datetime.now()

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        return model

    async def update(self, book_id: int, data: BookUpdate) -> Book:
        """Обновить книгу"""
        model = await self.get_by_id(book_id)

        update_data = data.model_dump(exclude_unset=True)

        # Проверяем внешние ключи, если они обновляются
        if "author_id" in update_data:
            await self._validate_author_exists(update_data["author_id"])

        for field, value in update_data.items():
            setattr(model, field, value)

        await self.session.commit()

        return await self.get_by_id(model.id)

    async def delete(self, book_id: int) -> None:
        """Удалить книгу (soft delete)"""
        model = await self.get_by_id(book_id)
        model.deleted_at = datetime.now()
        await self.session.commit()

    async def _validate_author_exists(self, author_id: int) -> None:
        """Проверить существование автора"""
        # todo оптимизировать (deleted_at - проверять на уровни бд)
        author = (await self.session.get(Author, author_id))
        if not author or author.deleted_at is not None:
            raise AuthorNotFoundError(author_id)

    # ==================== AUTHORS ====================
    async def get_all_authors(self, filters: AuthorFilterSchema) -> tuple[list[Author], int]:
        """
        Получить список авторов с фильтрацией и сортировкой

        Args:
            filters: Объект с параметрами фильтрации

        Returns:
            Кортеж (список авторов, всего записей в БД)
        """
        stmt = select(Author)

        # ✨ Фильтр по статусу удаления
        if filters.deleted == "active":
            stmt = stmt.where(Author.deleted_at.is_(None))
        elif filters.deleted == "deleted":
            stmt = stmt.where(Author.deleted_at.isnot(None))
        # elif filters.deleted == "all" — не добавляем условие, получаем всех

        # ✨ Поиск по имени
        if filters.search:
            stmt = stmt.where(Author.name.ilike(f"%{filters.search}%"))

        # ✨ Сортировка
        if filters.sort_by == "name":
            order_column = Author.name
        else:
            order_column = Author.name  # По умолчанию по имени

        if filters.sort_order.lower() == "desc":
            stmt = stmt.order_by(order_column.desc())
        else:
            stmt = stmt.order_by(order_column.asc())

        authors, total = await PaginationHelper.paginate(self.session, stmt, filters.skip, filters.limit)

        return authors, total

    async def get_author_by_id(self, author_id: int) -> Author:
        """Получить автора по ID"""
        stmt = (select(Author)
                .options(joinedload(Author.books))
                .where(Author.id == author_id))
        model = await self.session.scalar(stmt)
        if not model or model.deleted_at is not None:
            raise AuthorNotFoundError(author_id)
        return model

    async def create_author(self, data: AuthorCreate) -> Author:
        """Создать нового автора"""
        model = Author(**data.model_dump())
        self.session.add(model)
        await self.session.commit()

        model = await self.get_author_by_id(model.id)

        return model

    async def update_author(self, author_id: int, data: AuthorUpdate) -> Author:
        """Обновить автора"""
        model = await self.get_author_by_id(author_id)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(model, field, value)

        await self.session.commit()

        return await self.get_author_by_id(model.id)

    async def delete_author(self, author_id: int) -> None:
        """Удалить автора (soft delete)"""
        model = await self.get_author_by_id(author_id)
        model.deleted_at = datetime.now()
        await self.session.commit()

    async def restore_author(self, author_id: int) -> Author:
        """Восстановить удалённого автора"""
        stmt = select(Author).where(Author.id == author_id).where(Author.deleted_at.isnot(None))

        model = await self.session.scalar(stmt)
        if not model:
            raise AuthorNotFoundError(author_id)

        model.deleted_at = None
        await self.session.commit()

        return await self.get_author_by_id(model.id)

    async def force_delete_author(self, author_id: int) -> None:
        """Полностью удалить автора из БД (если уже был удалён)"""
        # Получаем даже удалённого автора
        stmt = select(Author).where(Author.id == author_id)
        author = await self.session.scalar(stmt)

        if not author:
            raise AuthorNotFoundError(author_id)

        # Проверяем, был ли он удалён (soft delete)
        if author.deleted_at is None:
            raise ValueError(f"Author {author_id} is not soft-deleted. Use delete() for soft delete.")

        # Полностью удаляем из БД
        await self.session.delete(author)
        await self.session.commit()
