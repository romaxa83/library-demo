from pydantic import BaseModel, ConfigDict, Field, field_validator, computed_field
from datetime import datetime
from typing import Dict, Any
from src.config import config


class MediaResponse(BaseModel):
    """Схема для представления медиа-файла в ответах API"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    path: str
    mimetype: str
    size: int
    entity_type: str
    entity_id: int
    thumbnails: Dict[str, str] | None = None
    created_at: datetime

    @computed_field
    @property
    def url(self) -> str:
        """Полный URL к оригинальному файлу"""
        return f"{config.app.url}{config.media.url_prefix}/{self.path}"

    @computed_field
    @property
    def thumbnail_urls(self) -> Dict[str, str]:
        """Словарь полных URL для превью"""
        if not self.thumbnails:
            return {}
        return {
            name: f"{config.app.url}{config.media.url_prefix}/{path}"
            for name, path in self.thumbnails.items()
        }


class ImageUploadValidation:
    """Логика валидации для загружаемых изображений"""

    ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

    @classmethod
    def validate(cls, content_type: str, size: int):
        if content_type not in cls.ALLOWED_MIME_TYPES:
            raise ValueError(f"Неподдерживаемый тип файла. Разрешены: {', '.join(cls.ALLOWED_MIME_TYPES)}")

        if size > cls.MAX_FILE_SIZE:
            raise ValueError(f"Файл слишком большой. Максимальный размер: {cls.MAX_FILE_SIZE // (1024 * 1024)}MB")