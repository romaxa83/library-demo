from fastapi import status

class TestCreateAuthor:
    """Тесты для создания автора"""

    def test_create_author_success(self, client):
        """Успешное создание автора"""
        author_data = {
            "name": "John Doe",
            "description": "Famous author"
        }

        response = client.post("/authors", json=author_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["name"] == author_data["name"]
        assert data["description"] == author_data["description"]
        assert "id" in data

    def test_create_author_without_description(self, client):
        """Создание автора без описания"""
        author_data = {
            "name": "Jane Smith"
        }

        response = client.post("/authors", json=author_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["name"] == author_data["name"]
        assert data["description"] is None

    def test_create_author_without_name(self, client):
        """Попытка создания автора без имени - должна быть ошибка"""
        author_data = {
            "description": "Some description"
        }

        response = client.post("/authors", json=author_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_author_empty_name(self, client):
        """Попытка создания автора с пустым именем"""
        author_data = {
            "name": "",
            "description": "Some description"
        }

        response = client.post("/authors", json=author_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_author_duplicate_name(self, client, author_factory):
        """Создание автора с существующим именем"""
        existing_author = author_factory(name="Duplicate Name")

        author_data = {
            "name": "Duplicate Name",
            "description": "Another author"
        }

        response = client.post("/authors", json=author_data)
        # Зависит от бизнес-логики - может быть 409 или 201
        # Предполагаем, что дубликаты имён разрешены
        assert response.status_code == status.HTTP_201_CREATED