from typing import Annotated
from fastapi import APIRouter, status, Depends

from src.media.dependencies import MediaServiceDep
from src.rbac.dependencies import PermissionRequired
from src.rbac.permissions import Permissions
from src.users.models import User

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.delete("/{media_id}", summary="Удалить файл", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    media_id: int,
    service: MediaServiceDep,
    user: Annotated[User, Depends(PermissionRequired(Permissions.MEDIA_DELETE))]
)->None:
    print("DELETE")

    await service.delete_media(media_id)



