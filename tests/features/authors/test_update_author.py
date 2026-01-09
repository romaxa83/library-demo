import pytest
from fastapi import status
from datetime import datetime
from src.rbac.permissions import Permissions


class TestUpdateAuthor:
    """Тесты для редактирования автора"""

    @pytest.mark.asyncio
    async def test_update_author_success(self, client, create_author, create_user, auth_header)->None:
        """Успешное обновление автора"""
        user = await create_user(permissions=[
            Permissions.AUTHOR_UPDATE.value
        ])
        header = await auth_header(user)

        author = await create_author(name="Old Name", description="Old description")

        update_data = {
            "name": "Updated Name",
            "description": "Updated description"
        }

        response = await client.patch(f"/authors/{author.id}", json=update_data, headers=header)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == author.id
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_update_author_partial(self, client, create_author, superadmin_user, auth_header)->None:
        """Частичное обновление автора (только имя)"""
        header = await auth_header(superadmin_user)

        author = await create_author(name="Old Name", description="Old description")

        update_data = {
            "name": "New Name"
        }

        response = await client.patch(f"/authors/{author.id}", json=update_data, headers=header)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == author.description

    @pytest.mark.asyncio
    async def test_update_author_not_found(self, client, superadmin_user, auth_header)->None:
        """Попытка обновить несуществующего автора"""
        header = await auth_header(superadmin_user)

        update_data = {
            "name": "New Name",
            "description": "New description"
        }

        response = await client.patch("/authors/99999", json=update_data, headers=header)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_deleted_author(self, client, create_author, superadmin_user, auth_header)->None:
        """Попытка обновить удалённого автора"""
        header = await auth_header(superadmin_user)

        author = await create_author(
            name="Deleted Author",
            deleted_at=datetime.now()
        )

        update_data = {
            "name": "Try to update"
        }

        response = await client.patch(f"/authors/{author.id}", json=update_data, headers=header)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_author_empty_name(self, client, create_author, superadmin_user, auth_header)->None:
        """Попытка обновить автора с пустым именем"""
        header = await auth_header(superadmin_user)

        author = await create_author()

        update_data = {
            "name": "",
            "description": "Valid description"
        }

        response = await client.patch(f"/authors/{author.id}", json=update_data, headers=header)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_not_perm(self, client, create_author, create_user, auth_header)->None:
        user = await create_user(permissions=[
            Permissions.AUTHOR_CREATE.value
        ])
        header = await auth_header(user)

        author = await create_author(name="Old Name", description="Old description")

        update_data = {
            "name": "Updated Name",
            "description": "Updated description"
        }

        response = await client.patch(f"/authors/{author.id}", json=update_data, headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_not_auth(self, client, create_author)->None:

        author = await create_author(name="Old Name", description="Old description")

        update_data = {
            "name": "Updated Name",
            "description": "Updated description"
        }

        response = await client.patch(f"/authors/{author.id}", json=update_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED