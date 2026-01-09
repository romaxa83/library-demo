import pytest
from datetime import datetime
from fastapi import status

from src.rbac.permissions import Permissions

class TestGetAuthors:
    """Тесты для получения списка авторов"""

    @pytest.mark.asyncio
    async def test_get_authors_empty_list(self, client, create_user, auth_header)->None:
        """Получить пустой список авторов"""
        user = await create_user(permissions=[Permissions.AUTHOR_LIST.value])
        header = await auth_header(user)

        response = await client.get("/authors", headers=header)

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
    async def test_get_authors_with_limit(self, client, create_authors, superadmin_user, auth_header)->None:
        """Получить авторов используя лимит"""
        header = await auth_header(superadmin_user)

        await create_authors(count=3)

        response = await client.get("/authors?skip=0&limit=2", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["data"]) == 2
        assert data["meta"]["total"] == 3
        assert data["meta"]["count"] == 2
        assert data["meta"]["per_page"] == 2
        assert data["meta"]["current_page"] == 1
        assert data["meta"]["total_pages"] == 2
        assert data["meta"]["skip"] == 0

    @pytest.mark.asyncio
    async def test_get_authors_with_skip(self, client, create_authors, superadmin_user, auth_header)->None:
        """Получить авторов используя skip"""
        header = await auth_header(superadmin_user)

        await create_authors(count=3)

        response = await client.get("/authors?skip=2&limit=2", headers=header)
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
    async def test_get_authors_with_search(self, client, create_author, superadmin_user, auth_header)->None:
        """Получить авторов с поиском"""
        header = await auth_header(superadmin_user)

        name = "John Doe"
        author = await create_author(name=name)
        await create_author(name="Tester")

        response = await client.get("/authors?search=John", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == author.name
        assert data["meta"]["total"] == 1

    @pytest.mark.asyncio
    async def test_get_authors_with_sort_asc(self, client, create_author, superadmin_user, auth_header)->None:
        """Получить авторов с сортировкой"""
        header = await auth_header(superadmin_user)

        author_1 = await create_author(name="Tom")
        author_2 = await create_author(name="Alen")
        author_3 = await create_author(name="John")

        response = await client.get("/authors?sort_by=name&sort_order=asc", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 3
        assert data["data"][0]["name"] == author_2.name
        assert data["data"][1]["name"] == author_3.name
        assert data["data"][2]["name"] == author_1.name

    @pytest.mark.asyncio
    async def test_get_authors_with_only_active(self, client, create_author, superadmin_user, auth_header)->None:
        """Получить авторов только активных (не удаленных)"""
        header = await auth_header(superadmin_user)

        author = await create_author()
        await create_author(deleted_at=datetime.now())

        response = await client.get("/authors", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == author.id

    @pytest.mark.asyncio
    async def test_get_authors_with_only_deleted(self, client, create_author, superadmin_user, auth_header)->None:
        """Получить авторов только удаленные"""
        header = await auth_header(superadmin_user)

        await create_author()
        deleted_author = await create_author(deleted_at=datetime.now())

        response = await client.get("/authors?deleted=deleted", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == deleted_author.id

    @pytest.mark.asyncio
    async def test_get_authors_with_all_status(self, client, create_author, superadmin_user, auth_header)->None:
        """Получить авторов и активных и удаленных"""
        header = await auth_header(superadmin_user)

        await create_author()
        await create_author(deleted_at=datetime.now())

        response = await client.get("/authors?deleted=all", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2

    @pytest.mark.asyncio
    async def test_not_perm(self, client, create_user, auth_header)->None:
        user = await create_user(permissions=[Permissions.AUTHOR_SHOW.value])
        header = await auth_header(user)

        response = await client.get("/authors", headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_not_auth(self, client)->None:
        response = await client.get("/authors")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED