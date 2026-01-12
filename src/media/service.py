import io
import uuid
from pathlib import Path

from fastapi import UploadFile
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from src.media.models import Media
from src.media.storage import LocalStorageBackend
from src.config import config


class MediaService:
    def __init__(self, session: AsyncSession):
        self.session = session
        # В будущем тут можно выбирать бэкенд на основе config.media.storage_type
        self.storage = LocalStorageBackend(config.media.root_path)

    async def upload_image(
        self,
        file: UploadFile,
        entity_type: str,
        entity_id: int
    ) -> Media:


        content = await file.read()
        file_ext = Path(file.filename).suffix
        folder = f"{entity_type}/{entity_id}"
        base_name = str(uuid.uuid4())

        # 1. Сохраняем оригинал
        original_path = f"{folder}/{base_name}{file_ext}"
        await self.storage.save(content, original_path)

        # 2. Генерируем превью
        thumbnails = {}
        for name, size in config.media.thumbnails.items():
            thumb_path = f"{folder}/{base_name}_{name}{file_ext}"
            thumb_content = self._create_thumbnail(content, size)
            await self.storage.save(thumb_content, thumb_path)
            thumbnails[name] = thumb_path

        # 3. Запись в БД
        media = Media(
            filename=file.filename,
            path=original_path,
            mimetype=file.content_type,
            size=len(content),
            entity_type=entity_type,
            entity_id=entity_id,
            thumbnails=thumbnails
        )
        self.session.add(media)
        await self.session.commit()
        await self.session.refresh(media)
        return media

    def _create_thumbnail(self, content: bytes, size: tuple[int, int]) -> bytes:
        img = Image.open(io.BytesIO(content))
        img.thumbnail(size)
        output = io.BytesIO()
        img.save(output, format=img.format)
        return output.getvalue()

    async def delete_media(self, media_id: int):

        media = await self.session.get(Media, media_id)
        if media:
            await self.storage.delete(media.path)
            if media.thumbnails:
                for path in media.thumbnails.values():
                    await self.storage.delete(path)
            await self.session.delete(media)
            await self.session.commit()