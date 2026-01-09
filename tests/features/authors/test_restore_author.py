import pytest
from fastapi import status
from datetime import datetime

from src.rbac.permissions import Permissions


class TestRestoreAuthor:
    """Тесты для восстановления удалённого автора"""

    @pytest.mark.asyncio
    async def test_restore_deleted_author_success(self, client, create_author, create_user, auth_header)->None:
        """Успешное восстановление удалённого автора"""
        user = await create_user(permissions=[
            Permissions.AUTHOR_SHOW.value,
            Permissions.AUTHOR_RESTORE.value,
        ])
        header = await auth_header(user)

        model = await create_author(deleted_at=datetime.now())

        response = await client.patch(f"/authors/{model.id}/restore", headers=header)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == model.id

        # Проверяем, что автор доступен
        get_response = await client.get(f"/authors/{model.id}", headers=header)
        assert get_response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_restore_active_author(self, client, create_author, superadmin_user, auth_header)->None:
        """Попытка восстановить активного (не удалённого) автора"""
        header = await auth_header(superadmin_user)

        author = await create_author()

        response = await client.patch(f"/authors/{author.id}/restore", headers=header)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_restore_nonexistent_author(self, client, superadmin_user, auth_header)->None:
        """Попытка восстановить несуществующего автора"""
        header = await auth_header(superadmin_user)

        response = await client.patch("/authors/99999/restore", headers=header)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_not_perm(self, client, create_author, create_user, auth_header)->None:
        user = await create_user(permissions=[
            Permissions.AUTHOR_SHOW.value
        ])
        header = await auth_header(user)

        model = await create_author(deleted_at=datetime.now())

        response = await client.patch(f"/authors/{model.id}/restore", headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_not_auth(self, client, create_author)->None:
        model = await create_author(deleted_at=datetime.now())

        response = await client.patch(f"/authors/{model.id}/restore")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED