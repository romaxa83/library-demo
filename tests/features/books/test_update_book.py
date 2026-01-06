from datetime import datetime
from fastapi import status

from src.rbac.permissions import Permissions


class TestUpdateBook:
    """Тесты для редактирования книги"""

    def test_update_book_success(self, client, create_book, create_user, auth_header)->None:
        """Успешное обновление книги (без автора)"""
        user = create_user(permissions=[Permissions.BOOK_UPDATE.value])
        header = auth_header(user)

        model = create_book(
            title="Old Title",
            description="Old description",
            page=22,
            is_available=False,
        )

        old_updated_at = model.updated_at

        _update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "page": 12,
            "is_available": True
        }

        response = client.patch(f"/books/{model.id}", json=_update_data, headers=header)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["id"] == model.id
        assert data["title"] == _update_data["title"]
        assert data["description"] == _update_data["description"]
        assert data["page"] == _update_data["page"]
        assert data["is_available"] == _update_data["is_available"]
        assert data["updated_at"] != old_updated_at

    def test_update_book_partial(self, client, create_book, superadmin_headers)->None:
        """Частичное обновление книги (только название)"""
        model = create_book(
            title="Old Title",
            description="Old description",
            page=22,
            is_available=False,
        )

        _update_data = {
            "title": "New Title"
        }

        response = client.patch(f"/books/{model.id}", json=_update_data, headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["title"] == _update_data["title"]
        assert data["description"] == model.description
        assert data["page"] == model.page
        assert data["is_available"] == model.is_available
        assert data["author_id"] == model.author_id

    def test_update_book_only_author(self, client, create_book, create_author, superadmin_headers)->None:
        """Частичное обновление книги (только автора)"""
        model = create_book()
        author = create_author()

        _update_data = {
            "author_id": author.id,
        }

        assert model.author_id != author.id

        response = client.patch(f"/books/{model.id}", json=_update_data, headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["author_id"] == model.author_id

    def test_update_book_only_author_not_exist(self, client, create_book, superadmin_headers)->None:
        """Частичное обновление книги (только автора которого не существует)"""
        model = create_book()

        _update_data = {
            "author_id": model.author_id + 1,
        }

        response = client.patch(f"/books/{model.id}", json=_update_data, headers=superadmin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        data = response.json()

        assert data["detail"] == f"Author with id {_update_data["author_id"]} not found"

    def test_update_book_only_author_deleted(self, client, create_book, create_author, superadmin_headers)->None:
        """Частичное обновление книги (только автора который удален)"""
        model = create_book()
        author = create_author(deleted_at=datetime.now())

        _update_data = {
            "author_id": author.id,
        }

        assert model.author_id != author.id

        response = client.patch(f"/books/{model.id}", json=_update_data, headers=superadmin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        data = response.json()

        assert data["detail"] == f"Author with id {_update_data["author_id"]} not found"

    def test_update_book_not_found(self, client, superadmin_headers)->None:
        """Попытка обновить несуществующую книгу"""
        _update_data = {
            "title": "title"
        }

        response = client.patch("/books/1", json=_update_data, headers=superadmin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Book with id 1 not found"

    def test_update_deleted_book(self, client, create_book, superadmin_headers)->None:
        """Попытка обновить удалённую книгу"""
        from datetime import datetime

        model = create_book(deleted_at=datetime.now())

        _update_data = {
            "title": "title"
        }

        response = client.patch(f"/books/{model.id}", json=_update_data, headers=superadmin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == f"Book with id {model.id} not found"

    def test_not_perm(self, client, create_book, create_user, auth_header)->None:
        user = create_user(permissions=[Permissions.BOOK_CREATE.value])
        header = auth_header(user)

        model = create_book()

        _update_data = {
            "title": "Updated Title"
        }

        response = client.patch(f"/books/{model.id}", json=_update_data, headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_not_auth(self, client, create_book)->None:
        model = create_book()

        _update_data = {
            "title": "Updated Title"
        }

        response = client.patch(f"/books/{model.id}", json=_update_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED