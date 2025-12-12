from fastapi import status
from datetime import datetime


class TestRestoreAuthor:
    """Тесты для восстановления удалённого автора"""

    def test_restore_deleted_author_success(self, client, create_author):
        """Успешное восстановление удалённого автора"""
        model = create_author(deleted_at=datetime.now())

        response = client.patch(f"/authors/{model.id}/restore")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == model.id

        # Проверяем, что автор доступен
        get_response = client.get(f"/authors/{model.id}")
        assert get_response.status_code == status.HTTP_200_OK

    def test_restore_active_author(self, client, create_author):
        """Попытка восстановить активного (не удалённого) автора"""
        author = create_author()

        response = client.patch(f"/authors/{author.id}/restore")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_restore_nonexistent_author(self, client):
        """Попытка восстановить несуществующего автора"""
        response = client.patch("/authors/99999/restore")
        assert response.status_code == status.HTTP_404_NOT_FOUND