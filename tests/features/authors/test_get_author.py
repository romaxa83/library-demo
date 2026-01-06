from datetime import datetime
from fastapi import status

from src.rbac.permissions import Permissions


class TestGetAuthor:
    """Тесты для получения автора"""

    def test_get_author_no_exist(self, client, superadmin_user, auth_header)->None:
        header = auth_header(superadmin_user)

        """Получить не существующего автора"""
        response = client.get("/authors/1", headers=header)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        assert data["detail"] == "Author with id 1 not found"
        # print(json.dumps(data, ensure_ascii=False, indent=2))

    def test_get_author_as_deleted(self, client, create_author, superadmin_user, auth_header)->None:
        """Получить удаленного автора"""
        header = auth_header(superadmin_user)

        author = create_author(deleted_at=datetime.now())

        response = client.get(f"/authors/{author.id}", headers=header)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        assert data["detail"] == f"Author with id {author.id} not found"

    def test_get_author(self, client, create_author, create_user, auth_header)->None:
        """Получить автора"""
        user = create_user(permissions=[Permissions.AUTHOR_SHOW.value])
        header = auth_header(user)

        author = create_author()

        response = client.get(f"/authors/{author.id}", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == author.id
        assert data["name"] == author.name
        assert data["description"] == author.description
        assert len(data["books"]) == 0

    def test_get_author_with_book(self, client, create_author, create_book, superadmin_user, auth_header)->None:
        """Получить автора с книгами"""
        header = auth_header(superadmin_user)

        author = create_author()
        create_book(author=author)
        create_book(author=author)

        response = client.get(f"/authors/{author.id}", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == author.id
        assert len(data["books"]) == 2

    def test_not_permission(self, client, create_author, create_user, auth_header)->None:
        user = create_user(permissions=[Permissions.AUTHOR_LIST.value])
        header = auth_header(user)

        author = create_author()

        response = client.get(f"/authors/{author.id}", headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_not_auth(self, client, create_author)->None:
        author = create_author()

        response = client.get(f"/authors/{author.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED