import pytest
from datetime import datetime
from fastapi import status

from src.rbac.permissions import Permissions


class TestGetBooks:
    """Тесты для получения списка книг"""

    @pytest.mark.asyncio
    async def test_get_books_empty_list(self, client, create_user, auth_header)->None:
        """Получить пустой список книг"""
        user = await create_user(permissions=[Permissions.BOOK_LIST.value])
        header = await auth_header(user)

        response = await client.get("/books", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["data"] == []
        assert data["meta"]["total"] == 0
        assert data["meta"]["count"] == 0
        assert data["meta"]["per_page"] == 10
        assert data["meta"]["current_page"] == 1
        assert data["meta"]["total_pages"] == 0
        assert data["meta"]["skip"] == 0

    @pytest.mark.asyncio
    async def test_get_books_with_limit(self, client, create_books, superadmin_headers)->None:
        """Получить книги, используя лимит"""

        await create_books(count=3)

        response = await client.get("/books?skip=0&limit=2", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # print(json.dumps(data, ensure_ascii=False, indent=2))
        assert len(data["data"]) == 2
        assert data["meta"]["total"] == 3
        assert data["meta"]["count"] == 2
        assert data["meta"]["per_page"] == 2
        assert data["meta"]["current_page"] == 1
        assert data["meta"]["total_pages"] == 2
        assert data["meta"]["skip"] == 0

    @pytest.mark.asyncio
    async def test_get_books_with_skip(self, client, create_books, superadmin_headers)->None:
        """Получить книги, используя skip"""

        await create_books(3)

        response = await client.get("/books?skip=2&limit=2", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["data"]) == 1
        assert data["meta"]["total"] == 3
        assert data["meta"]["count"] == 1
        assert data["meta"]["per_page"] == 2
        assert data["meta"]["current_page"] == 2
        assert data["meta"]["total_pages"] == 2
        assert data["meta"]["skip"] == 2

    @pytest.mark.asyncio
    async def test_get_book_with_search(self, client, create_book, superadmin_headers)->None:
        """Получить книгу с поиском по названию"""

        title = "Good book"
        model = await create_book(title=title)
        await create_book(title="Tester")

        response = await client.get("/books?search=book", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["title"] == model.title
        assert data["meta"]["total"] == 1

    @pytest.mark.asyncio
    async def test_get_book_with_author_id(self, client, create_book, create_author, superadmin_headers)->None:
        """Получить книги по автору"""

        author = await create_author()
        await create_book(author=author)
        await create_book(author=author)
        await create_book(title="Tester")

        response = await client.get(f"/books?author_id={author.id}", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # print(json.dumps(data, ensure_ascii=False, indent=2))
        assert len(data["data"]) == 2
        assert data["data"][0]["author_id"] == author.id
        assert data["data"][1]["author_id"] == author.id

    @pytest.mark.asyncio
    async def test_get_book_with_is_available_as_true(self, client, create_book, superadmin_headers)->None:
        """Получить книги по наличию"""

        await create_book(is_available=True)
        await create_book(is_available=False)
        await create_book(is_available=False)

        response = await client.get(f"/books?is_available=True", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_get_book_with_is_available_as_false(self, client, create_book, superadmin_headers)->None:
        """Получить книги по наличию"""

        await create_book(is_available=True)
        await create_book(is_available=False)
        await create_book(is_available=False)

        response = await client.get(f"/books?is_available=False", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2

    @pytest.mark.asyncio
    async def test_get_book_with_is_available_as_all(self, client, create_book, superadmin_headers)->None:
        """Получить книги по наличию"""

        await create_book(is_available=True)
        await create_book(is_available=False)
        await create_book(is_available=False)

        response = await client.get(f"/books", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 3

    @pytest.mark.asyncio
    async def test_get_books_with_only_active(self, client, create_book, superadmin_headers)->None:
        """Получить книг только активных (не удаленных)"""

        model = await create_book()
        await create_book(deleted_at=datetime.now())

        response = await client.get("/books", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == model.id

    @pytest.mark.asyncio
    async def test_get_books_with_only_deleted(self, client, create_book, superadmin_headers)->None:
        """Получить книги только удаленные"""

        await create_book()
        deleted_model = await create_book(deleted_at=datetime.now())

        response = await client.get("/books?deleted=deleted", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == deleted_model.id

    @pytest.mark.asyncio
    async def test_get_books_with_all_status(self, client, create_book, superadmin_headers)->None:
        """Получить книги и активных и удаленных"""

        await create_book()
        await create_book(deleted_at=datetime.now())

        response = await client.get("/books?deleted=all", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2

    @pytest.mark.asyncio
    async def test_get_books_with_sort_asc_as_title(self, client, create_book, superadmin_headers)->None:
        """Получить авторов с сортировкой по названию"""

        model_1 = await create_book(title="Tom")
        model_2 = await create_book(title="Alen")
        model_3 = await create_book(title="John")

        response = await client.get("/books?sort_by=title&sort_order=asc", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 3
        assert data["data"][0]["title"] == model_2.title
        assert data["data"][1]["title"] == model_3.title
        assert data["data"][2]["title"] == model_1.title

    @pytest.mark.asyncio
    async def test_get_books_with_sort_desc_as_title(self, client, create_book, superadmin_headers)->None:
        """Получить авторов с сортировкой по названию"""

        model_1 = await create_book(title="Tom")
        model_2 = await create_book(title="Alen")
        model_3 = await create_book(title="John")

        response = await client.get("/books?sort_by=title&sort_order=desc", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 3
        assert data["data"][0]["title"] == model_1.title
        assert data["data"][1]["title"] == model_3.title
        assert data["data"][2]["title"] == model_2.title

    @pytest.mark.asyncio
    async def test_get_books_with_sort_asc_as_page(self, client, create_book, superadmin_headers)->None:
        """Получить авторов с сортировкой по кол-ву страниц"""

        model_1 = await create_book(page=3)
        model_2 = await create_book(page=46)
        model_3 = await create_book(page=17)

        response = await client.get("/books?sort_by=page&sort_order=asc", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 3
        assert data["data"][0]["title"] == model_1.title
        assert data["data"][1]["title"] == model_3.title
        assert data["data"][2]["title"] == model_2.title

    @pytest.mark.asyncio
    async def test_get_books_with_sort_desc_as_page(self, client, create_book, superadmin_headers)->None:
        """Получить авторов с сортировкой по кол-ву страниц"""

        model_1 = await create_book(page=3)
        model_2 = await create_book(page=46)
        model_3 = await create_book(page=17)

        response = await client.get("/books?sort_by=page&sort_order=desc", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 3
        assert data["data"][0]["title"] == model_2.title
        assert data["data"][1]["title"] == model_3.title
        assert data["data"][2]["title"] == model_1.title

    @pytest.mark.asyncio
    async def test_not_perm(self, client, create_user, auth_header)->None:
        user = await create_user(permissions=[Permissions.BOOK_SHOW.value])
        header = await auth_header(user)

        response = await client.get("/books", headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_not_auth(self, client)->None:
        response = await client.get("/books")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED