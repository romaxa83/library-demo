import pytest
from datetime import datetime
from fastapi import status

from src.rbac.permissions import Permissions


class TestGetBook:
    """Тесты для получения книги"""

    @pytest.mark.asyncio
    async def test_get_book(self, client, create_book, create_author, create_user, auth_header)->None:
        """Получить книгу"""
        user = await create_user(permissions=[Permissions.BOOK_SHOW.value])
        header = await auth_header(user)

        author = await create_author()
        book = await create_book(author=author)

        response = await client.get(f"/books/{book.id}", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # print(json.dumps(data, ensure_ascii=False, indent=2))
        assert data["id"] == book.id
        assert data["title"] == book.title
        assert data["description"] == book.description
        assert data["page"] == book.page
        assert data["is_available"] == book.is_available

        assert data["created_at"] is not None
        assert data["updated_at"] is not None

        assert data["author_id"] == author.id
        assert data["author"]["id"] == author.id
        assert data["author"]["name"] == author.name
        assert data["author"]["description"] == author.description

    @pytest.mark.asyncio
    async def test_get_book_no_exist(self, client, superadmin_headers)->None:
        """Получить не существующею книгу"""
        response = await client.get("/books/1", headers=superadmin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        assert data["detail"] == "Book with id 1 not found"

    @pytest.mark.asyncio
    async def test_get_book_as_deleted(self, client, create_book, superadmin_headers)->None:
        """Получить удаленной книги"""

        book = await create_book(deleted_at=datetime.now())

        response = await client.get(f"/books/{book.id}", headers=superadmin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        assert data["detail"] == f"Book with id {book.id} not found"

    @pytest.mark.asyncio
    async def test_not_perm(self, client, create_book, create_author, create_user, auth_header)->None:
        user = await create_user(permissions=[Permissions.BOOK_LIST.value])
        header = await auth_header(user)

        author = await create_author()
        book = await create_book(author=author)

        response = await client.get(f"/books/{book.id}", headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_not_auth(self, client, create_book, create_author)->None:
        author = await create_author()
        book = await create_book(author=author)

        response = await client.get(f"/books/{book.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED