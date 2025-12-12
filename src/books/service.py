from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.books.exceptions import AuthorNotFoundError, BookNotFoundError
from src.books.models import Author, Book
from src.books.schemas import AuthorCreate, AuthorFilterSchema, AuthorUpdate, BookCreate, BookUpdate
from src.utils.pagination import PaginationHelper


class BookService:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Book]:
        """Получить список всех книг"""
        stmt = select(Book).options(selectinload(Book.author)).offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, book_id: int) -> Book:
        """Получить книгу по ID"""
        stmt = select(Book).options(selectinload(Book.author)).where(Book.id == book_id)
        book = self.session.scalar(stmt)
        if not book:
            raise BookNotFoundError(book_id)
        return book

    def create(self, data: BookCreate) -> Book:
        """Создать новую книгу"""
        # Проверяем существование автора и категории
        self._validate_author_exists(data.author_id)

        book = Book(**data.model_dump())
        self.session.add(book)
        self.session.commit()
        self.session.refresh(book)
        return book

    def update(self, book_id: int, data: BookUpdate) -> Book:
        """Обновить книгу"""
        book = self.get_by_id(book_id)

        update_data = data.model_dump(exclude_unset=True)

        # Проверяем внешние ключи, если они обновляются
        if "author_id" in update_data:
            self._validate_author_exists(update_data["author_id"])

        for field, value in update_data.items():
            setattr(book, field, value)

        self.session.commit()
        self.session.refresh(book)
        return book

    def delete(self, book_id: int) -> None:
        """Удалить книгу"""
        book = self.get_by_id(book_id)
        self.session.delete(book)
        self.session.commit()

    def _validate_author_exists(self, author_id: int) -> None:
        """Проверить существование автора"""
        author = self.session.get(Author, author_id)
        if not author:
            raise AuthorNotFoundError(author_id)

    # ==================== AUTHORS ====================
    def get_all_authors(self, filters: AuthorFilterSchema) -> tuple[list[Author], int]:
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

        authors, total = PaginationHelper.paginate(self.session, stmt, filters.skip, filters.limit)

        return authors, total

    def get_author_by_id(self, author_id: int) -> Author:
        """Получить автора по ID"""
        stmt = select(Author).where(Author.id == author_id)
        model = self.session.scalar(stmt)
        if not model or model.deleted_at is not None:
            raise AuthorNotFoundError(author_id)
        return model

    def create_author(self, data: AuthorCreate) -> Author:
        """Создать нового автора"""
        model = Author(**data.model_dump())
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model

    def update_author(self, author_id: int, data: AuthorUpdate) -> Author:
        """Обновить автора"""
        model = self.get_author_by_id(author_id)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(model, field, value)

        self.session.commit()
        self.session.refresh(model)
        return model

    def delete_author(self, author_id: int) -> None:
        """Удалить автора (soft delete)"""
        model = self.get_author_by_id(author_id)
        model.deleted_at = datetime.now()
        self.session.commit()

    def restore_author(self, author_id: int) -> Author:
        """Восстановить удалённого автора"""
        stmt = select(Author).where(Author.id == author_id).where(Author.deleted_at.isnot(None))
        author = self.session.scalar(stmt)
        if not author:
            raise AuthorNotFoundError(author_id)

        author.deleted_at = None
        self.session.commit()
        self.session.refresh(author)
        return author

    def force_delete_author(self, author_id: int) -> None:
        """Полностью удалить автора из БД (если уже был удалён)"""
        # Получаем даже удалённого автора
        stmt = select(Author).where(Author.id == author_id)
        author = self.session.scalar(stmt)

        if not author:
            raise AuthorNotFoundError(author_id)

        # Проверяем, был ли он удалён (soft delete)
        if author.deleted_at is None:
            raise ValueError(f"Author {author_id} is not soft-deleted. Use delete() for soft delete.")

        # Полностью удаляем из БД
        self.session.delete(author)
        self.session.commit()
