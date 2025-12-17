from fastapi import status
from datetime import datetime


class TestSoftDeleteBook:
    """Тесты для мягкого удаления книги"""

    def test_soft_delete_book_success(self, client, create_book):
        """Успешное мягкое удаление книги"""
        model = create_book()

        response = client.delete(f"/books/{model.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Проверяем, что книги помечен как удалённый, но запись осталась
        response = client.get("/books?deleted=deleted")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == model.id


    def test_soft_delete_nonexistent_book(self, client):
        """Попытка удалить несуществующею книгу"""
        response = client.delete("/books/1")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_soft_delete_already_deleted_author(self, client, create_book):
        """Попытка повторно удалить уже удалённую книгу"""
        model = create_book(deleted_at=datetime.now())

        response = client.delete(f"/books/{model.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND