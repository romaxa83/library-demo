import json
import pytest
from datetime import datetime
from fastapi import status


class TestGetAuthor:
    """Тесты для получения автора"""

    def test_get_author_no_exist(self, client):
        """Получить не существующего автора"""
        response = client.get("/authors/1")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        assert data["detail"] == "Author with id 1 not found"
        # print(json.dumps(data, ensure_ascii=False, indent=2))

    def test_get_author_as_deleted(self, client, create_author):
        """Получить удаленного автора"""

        author = create_author(deleted_at=datetime.now())

        response = client.get(f"/authors/{author.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        assert data["detail"] == f"Author with id {author.id} not found"

    def test_get_author(self, client, create_author):
        """Получить автора"""

        author = create_author()

        response = client.get(f"/authors/{author.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == author.id
        assert data["name"] == author.name
        assert data["description"] == author.description
        assert len(data["books"]) == 0

    def test_get_author_with_book(self, client, create_author, create_book):
        """Получить автора с книгами"""

        author = create_author()
        create_book(author=author)
        create_book(author=author)

        response = client.get(f"/authors/{author.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == author.id
        assert len(data["books"]) == 2