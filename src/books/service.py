from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from src.books.models import Book, Author, Category
from src.books.schemas import BookCreate, BookUpdate
from src.books.exceptions import BookNotFoundError, AuthorNotFoundError, CategoryNotFoundError

class BookService:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Book]:
        """Получить список всех книг"""
        stmt = (
            select(Book)
            .options(selectinload(Book.author), selectinload(Book.category))
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, book_id: int) -> Book:
        """Получить книгу по ID"""
        stmt = (
            select(Book)
            .options(selectinload(Book.author), selectinload(Book.category))
            .where(Book.id == book_id)
        )
        book = self.session.scalar(stmt)
        if not book:
            raise BookNotFoundError(book_id)
        return book

    def create(self, data: BookCreate) -> Book:
        """Создать новую книгу"""
        # Проверяем существование автора и категории
        self._validate_author_exists(data.author_id)
        self._validate_category_exists(data.category_id)

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
        if "category_id" in update_data:
            self._validate_category_exists(update_data["category_id"])

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

    def _validate_category_exists(self, category_id: int) -> None:
        """Проверить существование категории"""
        category = self.session.get(Category, category_id)
        if not category:
            raise CategoryNotFoundError(category_id)