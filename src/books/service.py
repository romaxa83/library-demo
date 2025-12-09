from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from src.books.models import Book, Author
from src.books.schemas import BookCreate, BookUpdate, AuthorCreate, AuthorUpdate
from src.books.exceptions import BookNotFoundError, AuthorNotFoundError

class BookService:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Book]:
        """Получить список всех книг"""
        stmt = (
            select(Book)
            .options(selectinload(Book.author))
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, book_id: int) -> Book:
        """Получить книгу по ID"""
        stmt = (
            select(Book)
            .options(selectinload(Book.author))
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
    def get_all_authors(self, skip: int = 0, limit: int = 100) -> list[Author]:
        """Получить список всех авторов"""
        stmt = select(Author).offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all())

    def get_author_by_id(self, author_id: int) -> Author:
        """Получить автора по ID"""
        stmt = (
            select(Author)
            .where(Author.id == author_id)
        )
        model = self.session.scalar(stmt)
        if not model:
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
        """Удалить автора"""
        model = self.get_author_by_id(author_id)
        self.session.delete(model)
        self.session.commit()