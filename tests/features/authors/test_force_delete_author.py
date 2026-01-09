import pytest
from fastapi import status
from datetime import datetime

from src.rbac.permissions import Permissions


class TestForceDeleteAuthor:
    """Тесты для жёсткого (полного) удаления автора"""

    @pytest.mark.asyncio
    async def test_force_delete_author_success(self, client, create_author, create_user, auth_header)->None:
        user = await create_user(permissions=[
            Permissions.AUTHOR_LIST.value,
            Permissions.AUTHOR_FORCE_DELETE.value
        ])
        header = await auth_header(user)

        """Успешное полное удаление автора"""
        author = await create_author(deleted_at=datetime.now())
        author_id = author.id

        # смотрим что автор есть в архиве (уже мягко удален)
        response = await client.get("/authors?deleted=deleted", headers=header)
        data = response.json()

        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == author_id

        # удаляем
        response = await client.delete(f"/authors/{author_id}/force", headers=header)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # смотрим что автор нет в архиве
        response = await client.get("/authors?deleted=deleted", headers=header)
        data = response.json()
        assert len(data["data"]) == 0

    # def test_force_delete_active_author(self, client, create_author, superadmin_user, auth_header):
    #     """Попытка удалить активного автора"""
    #     header = auth_header(superadmin_user)
    #
    #     author = create_author()
    #
    #     # удаляем
    #     response = client.delete(f"/authors/{author.id}/force", headers=header)
    #     print(response)
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_force_delete_nonexistent_author(self, client, superadmin_user, auth_header)->None:
        """Попытка полностью удалить несуществующего автора"""
        header = await auth_header(superadmin_user)

        response = await client.delete("/authors/99999/force", headers=header)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_not_perm(self, client, create_author, create_user, auth_header)->None:
        user = await create_user(permissions=[
            Permissions.AUTHOR_LIST.value
        ])
        header = await auth_header(user)

        author = await create_author(deleted_at=datetime.now())

        # удаляем
        response = await client.delete(f"/authors/{author.id}/force", headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_not_auth(self, client, create_author)->None:
        author = await create_author(deleted_at=datetime.now())

        # удаляем
        response = await client.delete(f"/authors/{author.id}/force")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED