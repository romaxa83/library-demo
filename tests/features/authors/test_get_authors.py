import json
import pytest
from datetime import datetime
from fastapi import status


class TestGetAuthors:
    """Тесты для получения списка авторов"""

    def test_get_authors_empty_list(self, client):
        """Получить пустой список авторов"""
        response = client.get("/authors")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["data"] == []
        assert data["meta"]["total"] == 0
        assert data["meta"]["count"] == 0
        assert data["meta"]["per_page"] == 10
        assert data["meta"]["current_page"] == 1
        assert data["meta"]["total_pages"] == 0
        assert data["meta"]["skip"] == 0

    def test_get_authors_with_limit(self, client, create_authors):
        """Получить авторов используя лимит"""

        create_authors(count=3)

        response = client.get("/authors?skip=0&limit=2")
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

    def test_get_authors_with_skip(self, client, create_authors):
        """Получить авторов используя skip"""

        create_authors(count=3)

        response = client.get("/authors?skip=0&limit=2&skip=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["data"]) == 1
        assert data["meta"]["total"] == 3
        assert data["meta"]["count"] == 1
        assert data["meta"]["per_page"] == 2
        assert data["meta"]["current_page"] == 2
        assert data["meta"]["total_pages"] == 2
        assert data["meta"]["skip"] == 2

    def test_get_authors_with_search(self, client, create_author):
        """Получить авторов с поиском"""

        name = "John Doe"
        author = create_author(name=name)
        create_author(name="Tester")

        response = client.get("/authors?search=John")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == author.name
        assert data["meta"]["total"] == 1

    def test_get_authors_with_sort_asc(self, client, create_author):
        """Получить авторов с сортировкой"""

        author_1 = create_author(name="Tom")
        author_2 = create_author(name="Alen")
        author_3 = create_author(name="John")

        response = client.get("/authors?sort_by=name&sort_order=asc")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 3
        assert data["data"][0]["name"] == author_2.name
        assert data["data"][1]["name"] == author_3.name
        assert data["data"][2]["name"] == author_1.name

    def test_get_authors_with_only_active(self, client, create_author):
        """Получить авторов только активных (не удаленных)"""

        author = create_author()
        create_author(deleted_at=datetime.now())

        response = client.get("/authors")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == author.id

    def test_get_authors_with_only_deleted(self, client, create_author):
        """Получить авторов только удаленные"""

        create_author()
        deleted_author = create_author(deleted_at=datetime.now())

        response = client.get("/authors?deleted=deleted")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == deleted_author.id

    def test_get_authors_with_all_status(self, client, create_author):
        """Получить авторов и активных и удаленных"""

        create_author()
        create_author(deleted_at=datetime.now())

        response = client.get("/authors?deleted=all")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2