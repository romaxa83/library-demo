from typing import Annotated
from fastapi import Depends

from src.database import DbSessionDep
from src.media.service import MediaService


def get_media_service(session: DbSessionDep) -> MediaService:
    return MediaService(session)

# Type alias для удобства
MediaServiceDep = Annotated[MediaService, Depends(get_media_service)]