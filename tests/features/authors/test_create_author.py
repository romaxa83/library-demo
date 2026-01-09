import pytest
from fastapi import status
from src.rbac.permissions import Permissions

class TestCreateAuthor:
    """Тесты для создания автора"""

    @pytest.mark.asyncio
    async def test_create_author_success(self, client, create_user, auth_header)->None:
        user = await create_user(permissions=[Permissions.AUTHOR_CREATE.value])
        header = await auth_header(user)

        """Успешное создание автора"""
        author_data = {
            "name": "John Doe",
            "description": "Famous author"
        }

        response = await client.post("/authors", json=author_data, headers=header)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["name"] == author_data["name"]
        assert data["description"] == author_data["description"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_author_without_description(self, client, superadmin_user, auth_header)->None:
        """Создание автора без описания"""

        header = await auth_header(superadmin_user)

        author_data = {
            "name": "Jane Smith"
        }

        response = await client.post("/authors", json=author_data, headers=header)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["name"] == author_data["name"]
        assert data["description"] is None

    @pytest.mark.asyncio
    async def test_create_author_without_name(self, client, superadmin_user, auth_header)->None:
        header = await auth_header(superadmin_user)

        """Попытка создания автора без имени - должна быть ошибка"""
        author_data = {
            "description": "Some description"
        }

        response = await client.post("/authors", json=author_data, headers=header)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_create_author_empty_name(self, client, superadmin_user, auth_header)->None:
        header = await auth_header(superadmin_user)

        """Попытка создания автора с пустым именем"""
        author_data = {
            "name": "",
            "description": "Some description"
        }

        response = await client.post("/authors", json=author_data, headers=header)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_create_author_duplicate_name(self, client, author_factory, superadmin_user, auth_header)->None:
        header = await auth_header(superadmin_user)

        """Создание автора с существующим именем"""
        await author_factory(name="Duplicate Name")

        author_data = {
            "name": "Duplicate Name",
            "description": "Another author"
        }

        response = await client.post("/authors", json=author_data, headers=header)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_create_author_not_permission(self, client, create_user, auth_header)->None:
        user = await create_user(permissions=[Permissions.AUTHOR_SHOW.value])
        header = await auth_header(user)

        """Успешное создание автора"""
        author_data = {
            "name": "John Doe",
            "description": "Famous author"
        }

        response = await client.post("/authors", json=author_data, headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_create_author_not_auth(self, client)->None:
        author_data = {
            "name": "John Doe",
            "description": "Famous author"
        }

        response = await client.post("/authors", json=author_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
