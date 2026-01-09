import pytest
from fastapi import status
from datetime import datetime

from src.rbac.permissions import Permissions


class TestSoftDeleteBook:
    """Тесты для мягкого удаления книги"""

    @pytest.mark.asyncio
    async def test_soft_delete_book_success(self, client, create_book, create_user, auth_header)->None:
        """Успешное мягкое удаление книги"""
        user = await create_user(permissions=[
            Permissions.BOOK_LIST.value,
            Permissions.BOOK_DELETE.value
        ])
        header = await auth_header(user)

        model = await create_book()

        response = await client.delete(f"/books/{model.id}", headers=header)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Проверяем, что книги помечен как удалённый, но запись осталась
        response = await client.get("/books?deleted=deleted", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == model.id

    @pytest.mark.asyncio
    async def test_soft_delete_nonexistent_book(self, client, superadmin_headers)->None:
        """Попытка удалить несуществующею книгу"""
        response = await client.delete("/books/1", headers=superadmin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_soft_delete_already_deleted_author(self, client, create_book, superadmin_headers)->None:
        """Попытка повторно удалить уже удалённую книгу"""
        model = await create_book(deleted_at=datetime.now())

        response = await client.delete(f"/books/{model.id}", headers=superadmin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_not_perm(self, client, create_book, create_user, auth_header)->None:
        user = await create_user(permissions=[
            Permissions.BOOK_LIST.value
        ])
        header = await auth_header(user)

        model = await create_book()

        response = await client.delete(f"/books/{model.id}", headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_not_auth(self, client, create_book)->None:
        model = await create_book()

        response = await client.delete(f"/books/{model.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED