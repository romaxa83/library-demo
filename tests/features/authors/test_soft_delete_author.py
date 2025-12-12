from fastapi import status
from datetime import datetime


class TestSoftDeleteAuthor:
    """Тесты для мягкого удаления автора"""

    def test_soft_delete_author_success(self, client, create_author):
        """Успешное мягкое удаление автора"""
        author = create_author()

        response = client.delete(f"/authors/{author.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Проверяем, что автор помечен как удалённый но запись осталась
        response = client.get("/authors?deleted=deleted")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == author.id

    def test_soft_delete_nonexistent_author(self, client):
        """Попытка удалить несуществующего автора"""
        response = client.delete("/authors/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_soft_delete_already_deleted_author(self, client, create_author):
        """Попытка повторно удалить уже удалённого автора"""
        author = create_author(deleted_at=datetime.now())

        response = client.delete(f"/authors/{author.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND