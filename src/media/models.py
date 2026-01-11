from datetime import datetime
from sqlalchemy import String, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(String(500))  # Путь к оригиналу
    mimetype: Mapped[str] = mapped_column(String(100))
    size: Mapped[int] = mapped_column(Integer)  # Размер в байтах

    # Полиморфная связь
    entity_type: Mapped[str] = mapped_column(String(100))  # 'book', 'user', etc.
    entity_id: Mapped[int] = mapped_column(Integer)

    # Хранение путей к превью: {"small": "path/to/small.jpg", ...}
    thumbnails: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)