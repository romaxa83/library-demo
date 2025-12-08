from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, func


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Связь один ко многим: у автора много книг
    books: Mapped[list["Book"]] = relationship("Book", back_populates="author")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Связь один ко многим: в категории много книг
    books: Mapped[list["Book"]] = relationship(back_populates="category")


class Book(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    page: Mapped[int] = mapped_column(Integer, default=0)

    # Внешние ключи
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('authors.id'))
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )