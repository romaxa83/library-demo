from fastapi import status


class TestUpdateAuthor:
    """Тесты для редактирования автора"""

    def test_update_author_success(self, client, create_author):
        """Успешное обновление автора"""

        author = create_author(name="Old Name", description="Old description")

        update_data = {
            "name": "Updated Name",
            "description": "Updated description"
        }

        response = client.patch(f"/authors/{author.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == author.id
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    def test_update_author_partial(self, client, create_author):
        """Частичное обновление автора (только имя)"""
        author = create_author(name="Old Name", description="Old description")

        update_data = {
            "name": "New Name"
        }

        response = client.patch(f"/authors/{author.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == author.description

    def test_update_author_not_found(self, client):
        """Попытка обновить несуществующего автора"""
        update_data = {
            "name": "New Name",
            "description": "New description"
        }

        response = client.patch("/authors/99999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_deleted_author(self, client, create_author):
        """Попытка обновить удалённого автора"""
        from datetime import datetime

        author = create_author(
            name="Deleted Author",
            deleted_at=datetime.now()
        )

        update_data = {
            "name": "Try to update"
        }

        response = client.patch(f"/authors/{author.id}", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_author_empty_name(self, client, create_author):
        """Попытка обновить автора с пустым именем"""
        author = create_author()

        update_data = {
            "name": "",
            "description": "Valid description"
        }

        response = client.patch(f"/authors/{author.id}", json=update_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT