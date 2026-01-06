from fastapi import status
from datetime import datetime

from src.rbac.permissions import Permissions


class TestRestoreAuthor:
    """Тесты для восстановления удалённого автора"""

    def test_restore_deleted_author_success(self, client, create_author, create_user, auth_header)->None:
        """Успешное восстановление удалённого автора"""
        user = create_user(permissions=[
            Permissions.AUTHOR_SHOW.value,
            Permissions.AUTHOR_RESTORE.value,
        ])
        header = auth_header(user)

        model = create_author(deleted_at=datetime.now())

        response = client.patch(f"/authors/{model.id}/restore", headers=header)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == model.id

        # Проверяем, что автор доступен
        get_response = client.get(f"/authors/{model.id}", headers=header)
        assert get_response.status_code == status.HTTP_200_OK

    def test_restore_active_author(self, client, create_author, superadmin_user, auth_header)->None:
        """Попытка восстановить активного (не удалённого) автора"""
        header = auth_header(superadmin_user)

        author = create_author()

        response = client.patch(f"/authors/{author.id}/restore", headers=header)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_restore_nonexistent_author(self, client, superadmin_user, auth_header)->None:
        """Попытка восстановить несуществующего автора"""
        header = auth_header(superadmin_user)

        response = client.patch("/authors/99999/restore", headers=header)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_not_perm(self, client, create_author, create_user, auth_header)->None:
        user = create_user(permissions=[
            Permissions.AUTHOR_SHOW.value
        ])
        header = auth_header(user)

        model = create_author(deleted_at=datetime.now())

        response = client.patch(f"/authors/{model.id}/restore", headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_not_auth(self, client, create_author)->None:
        model = create_author(deleted_at=datetime.now())

        response = client.patch(f"/authors/{model.id}/restore")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED