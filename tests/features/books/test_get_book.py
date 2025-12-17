from datetime import datetime
from fastapi import status
import json


class TestGetBook:
    """Тесты для получения книги"""

    def test_get_book(self, client, create_book, create_author):
        """Получить книгу"""

        author = create_author()
        book = create_book(author=author)

        response = client.get(f"/books/{book.id}")
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

    def test_get_book_no_exist(self, client):
        """Получить не существующею книгу"""
        response = client.get("/books/1")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        assert data["detail"] == "Book with id 1 not found"

    def test_get_book_as_deleted(self, client, create_book):
        """Получить удаленной книги"""

        book = create_book(deleted_at=datetime.now())

        response = client.get(f"/books/{book.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        assert data["detail"] == f"Book with id {book.id} not found"

