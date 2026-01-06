from fastapi import status
from datetime import datetime

from src.rbac.permissions import Permissions


class TestSoftDeleteAuthor:
    """Тесты для мягкого удаления автора"""

    def test_soft_delete_author_success(self, client, create_author, create_user, auth_header)->None:
        """Успешное мягкое удаление автора"""
        user = create_user(permissions=[
            Permissions.AUTHOR_DELETE.value,
            Permissions.AUTHOR_LIST.value,
        ])
        header = auth_header(user)

        author = create_author()

        response = client.delete(f"/authors/{author.id}", headers=header)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Проверяем, что автор помечен как удалённый, но запись осталась
        response = client.get("/authors?deleted=deleted", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == author.id

    def test_soft_delete_nonexistent_author(self, client, superadmin_user, auth_header)->None:
        """Попытка удалить несуществующего автора"""
        header = auth_header(superadmin_user)

        response = client.delete("/authors/99999", headers=header)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_soft_delete_already_deleted_author(self, client, create_author, superadmin_user, auth_header)->None:
        """Попытка повторно удалить уже удалённого автора"""
        header = auth_header(superadmin_user)

        author = create_author(deleted_at=datetime.now())

        response = client.delete(f"/authors/{author.id}", headers=header)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_not_perm(self, client, create_author, create_user, auth_header)->None:
        user = create_user(permissions=[
            Permissions.AUTHOR_LIST.value,
        ])
        header = auth_header(user)

        author = create_author()

        response = client.delete(f"/authors/{author.id}", headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_not_auth(self, client, create_author)->None:
        author = create_author()

        response = client.delete(f"/authors/{author.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED