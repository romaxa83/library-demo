"""Утилиты для работы с пагинацией"""

from typing import Generic, Tuple, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

T = TypeVar("T")  # Generic тип для моделей


class PaginationMeta(BaseModel):
    """Метаданные пагинации"""

    total: int = Field(description="Всего записей в БД")
    count: int = Field(description="Количество записей в текущем ответе")
    per_page: int = Field(description="Записей на странице")
    current_page: int = Field(description="Текущая страница")
    total_pages: int = Field(description="Всего страниц")
    skip: int = Field(description="Количество пропущенных записей")


class PaginatedResponse(BaseModel, Generic[T]):
    """Пагинированный ответ для любой сущности"""

    data: list[T] = Field(description="Данные")
    meta: PaginationMeta = Field(description="Метаданные пагинации")

    model_config = ConfigDict(from_attributes=True)


class PaginationParams:
    """Параметры пагинации"""

    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit

    def get_current_page(self) -> int:
        """Получить номер текущей страницы"""
        return (self.skip // self.limit) + 1

    def get_total_pages(self, total: int) -> int:
        """Получить всего страниц"""
        return (total + self.limit - 1) // self.limit


class PaginationHelper:
    """Помощник для работы с пагинацией"""

    @staticmethod
    async def paginate(
            session: AsyncSession,
            stmt: Select,
            skip: int = 0,
            limit: int = 10
    ) -> Tuple[list, int]:
        """
        Выполнить пагинированный запрос

        Args:
            session: SQLAlchemy сессия
            stmt: SQL выражение select
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            Кортеж (список записей, всего записей в БД)
        """
        # ✨ Создаём отдельный запрос для подсчёта БЕЗ ORDER BY
        # Используем order_by(None) чтобы очистить сортировку

        count_stmt = stmt.order_by(None).with_only_columns(func.count())
        total: int = await session.scalar(count_stmt) or 0

        # ✨ Применяем пагинацию к исходному запросу (с сортировкой)
        paginated_stmt = stmt.offset(skip).limit(limit)

        results = list((await session.scalars(paginated_stmt)).all())

        return results, total

    @staticmethod
    def build_pagination_meta(total: int, skip: int, limit: int) -> PaginationMeta:
        """
        Построить метаданные пагинации

        Args:
            total: Всего записей
            skip: Количество пропущенных записей
            limit: Записей на странице

        Returns:
            Объект PaginationMeta
        """
        current_page = (skip // limit) + 1
        total_pages = (total + limit - 1) // limit

        return PaginationMeta(
            total=total,
            count=min(limit, total - skip),  # Реальное количество в ответе
            per_page=limit,
            current_page=current_page,
            total_pages=total_pages,
            skip=skip,
        )

    @staticmethod
    def build_paginated_response(data: list[T], total: int, skip: int, limit: int) -> PaginatedResponse[T]:
        """
        Построить пагинированный ответ

        Args:
            data: Список данных
            total: Всего записей
            skip: Количество пропущенных записей
            limit: Записей на странице

        Returns:
            Объект PaginatedResponse
        """
        meta = PaginationHelper.build_pagination_meta(total, skip, limit)
        return PaginatedResponse(data=data, meta=meta)
