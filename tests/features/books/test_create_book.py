from fastapi import status
import pytest
from pygments.lexers import data

from src.rbac.permissions import Permissions


class TestCreateBook:
    """Тесты для создания книги"""

    @pytest.mark.asyncio
    async def test_create_book_success(self, client, create_author, create_user, auth_header)->None:
        """Успешное создание книги"""
        user = await create_user(permissions=[Permissions.BOOK_CREATE.value])
        header = await auth_header(user)

        author = await create_author()

        _data = {
            "title": "test title",
            "description": "test description",
            "page": 23,
            "is_available": True,
            "author_id": author.id,
        }

        response = await client.post("/books", json=_data, headers=header)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()

        assert "id" in data
        assert "created_at" in data
        assert data["title"] == _data["title"]
        assert data["description"] == _data["description"]
        assert data["page"] == _data["page"]
        assert data["is_available"] == _data["is_available"]
        assert data["author_id"] == _data["author_id"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

    @pytest.mark.asyncio
    async def test_create_book_only_required_fields(self, client, create_author, superadmin_headers)->None:
        """Успешное создание книги только с обязательными полями"""

        author = await create_author()

        _data = {
            "title": "test title",
            "author_id": author.id,
        }

        response = await client.post("/books", json=_data, headers=superadmin_headers)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()

        assert "id" in data
        assert data["description"] is None
        assert data["page"] == 0
        assert data["is_available"] == True

    @pytest.mark.asyncio
    async def test_create_book_without_title(self, client, create_author, superadmin_headers)->None:
        """Попытка создания книги без названия - должна быть ошибка"""
        author = await create_author()

        _data = {
            "author_id": author.id,
        }

        response = await client.post("/books", json=_data, headers=superadmin_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_create_book_without_author(self, client, superadmin_headers)->None:
        """Попытка создания книгу без автора"""
        _data = {
            "title": "test title"
        }

        response = await client.post("/books", json=_data, headers=superadmin_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_create_book_duplicate_title(self, client,create_book, superadmin_headers)->None:
        """Создание книги с существующим названием (должна быть ошибка)"""
        book = await create_book()

        _data = {
            "title": book.title,
            "author_id": book.author_id,
        }

        response = await client.post("/books", json=_data, headers=superadmin_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_create_book_empty_title(self, client, create_author, superadmin_headers)->None:
        """Создание книги с пустым названием (должна быть ошибка)"""
        author = await create_author()

        _data = {
            "title": "",
            "author_id": author.id,
        }

        response = await client.post("/books", json=_data, headers=superadmin_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        data = response.json()

        assert data['detail'][0]['type'] == 'string_too_short'
        assert data['detail'][0]['msg'] == 'String should have at least 1 character'

    @pytest.mark.asyncio
    async def test_create_book_not_exist_author(self, client, superadmin_headers)->None:
        """Создание книги с несуществующим автором (должна быть ошибка)"""

        _data = {
            "title": "test_title",
            "author_id": 99999,
        }

        response = await client.post("/books", json=_data, headers=superadmin_headers)

        # assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        data = response.json()

        assert data['detail'] == 'Author with id 99999 not found'

    @pytest.mark.asyncio
    async def test_not_perm(self, client, create_author, create_user, auth_header)->None:
        user = await create_user(permissions=[Permissions.BOOK_SHOW.value])
        header = await auth_header(user)

        author = await create_author()

        _data = {
            "title": "test title",
            "description": "test description",
            "page": 23,
            "is_available": True,
            "author_id": author.id,
        }

        response = await client.post("/books", json=_data, headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_not_auth(self, client, create_author)->None:
        author = await create_author()

        _data = {
            "title": "test title",
            "description": "test description",
            "page": 23,
            "is_available": True,
            "author_id": author.id,
        }

        response = await client.post("/books", json=_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED