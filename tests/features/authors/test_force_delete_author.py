from fastapi import status
from datetime import datetime


class TestForceDeleteAuthor:
    """Тесты для жёсткого (полного) удаления автора"""

    def test_force_delete_author_success(self, client, create_author):
        """Успешное полное удаление автора"""
        author = create_author(deleted_at=datetime.now())
        author_id = author.id

        # смотрим что автор есть в архиве (уже мягко удален)
        response = client.get("/authors?deleted=deleted")
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == author_id

        # удаляем
        response = client.delete(f"/authors/{author_id}/force")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # смотрим что автор нет в архиве
        response = client.get("/authors?deleted=deleted")
        data = response.json()
        assert len(data["data"]) == 0

    # def test_force_delete_active_author(self, client, create_author):
    #     """Попытка удалить активного автора"""
    #     author = create_author()
    #
    #     # удаляем
    #     response = client.delete(f"/authors/{author.id}/force")
    #     assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_force_delete_nonexistent_author(self, client):
        """Попытка полностью удалить несуществующего автора"""
        response = client.delete("/authors/99999/force")
        assert response.status_code == status.HTTP_404_NOT_FOUND
