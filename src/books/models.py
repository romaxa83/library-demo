from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.media.models import Media

BOOK_MORPH_NAME = "book"

class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Связь один ко многим: у автора много книг
    books: Mapped[list["Book"]] = relationship("Book", back_populates="author")

    @property
    def is_deleted(self) -> bool:
        """Проверить, удалена ли запись"""
        return self.deleted_at is not None


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    page: Mapped[int] = mapped_column(Integer, default=0)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    # Внешние ключи
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("authors.id"))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Связь "многие к одному" с Author
    author: Mapped["Author"] = relationship("Author", back_populates="books")

    # Полиморфная связь для картинок
    images: Mapped[list["Media"]] = relationship(
        "Media",
        primaryjoin="and_(Book.id == foreign(remote(Media.entity_id)), Media.entity_type == 'book')",
        viewonly=True,
        # Позволяет подгружать через .options(selectinload(Book.images))
        lazy="select"
    )

    @property
    def is_deleted(self) -> bool:
        """Проверить, удалена ли запись"""
        return self.deleted_at is not None
