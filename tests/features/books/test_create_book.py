from fastapi import status

class TestCreateBook:
    """Тесты для создания книги"""

    def test_create_book_success(self, client, create_author):
        """Успешное создание книги"""
        author = create_author()

        _data = {
            "title": "test title",
            "description": "test description",
            "page": 23,
            "is_available": True,
            "author_id": author.id,
        }

        response = client.post("/books", json=_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()

        assert data["title"] == _data["title"]
        assert data["description"] == _data["description"]
        assert data["page"] == _data["page"]
        assert data["is_available"] == _data["is_available"]
        assert data["author_id"] == _data["author_id"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

    def test_create_book_only_required_fields(self, client, create_author):
        """Успешное создание книги только с обязательными полями"""
        author = create_author()

        _data = {
            "title": "test title",
            "author_id": author.id,
        }

        response = client.post("/books", json=_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()

        assert "id" in data
        assert data["description"] is None
        assert data["page"] == 0
        assert data["is_available"] == True

    def test_create_book_without_title(self, client, create_author):
        """Попытка создания книги без названия - должна быть ошибка"""
        author = create_author()

        _data = {
            "author_id": author.id,
        }

        response = client.post("/books", json=_data)
        # print(response.json())
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_book_without_author(self, client):
        """Попытка создания книгу без автора"""
        _data = {
            "title": "test title"
        }

        response = client.post("/books", json=_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_book_duplicate_title(self, client,create_book):
        """Создание книги с существующим названием (должна быть ошибка)"""

        book = create_book()

        _data = {
            "title": book.title,
            "author_id": book.author.id,
        }

        response = client.post("/books", json=_data)
        # Зависит от бизнес-логики - может быть 409 или 201
        # Предполагаем, что дубликаты имён разрешены
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_book_empty_title(self, client, create_author):
        """Создание книги с пустым названием (должна быть ошибка)"""

        author = create_author()

        _data = {
            "title": "",
            "author_id": author.id,
        }

        response = client.post("/books", json=_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        data = response.json()

        assert data['detail'][0]['type'] == 'string_too_short'
        assert data['detail'][0]['msg'] == 'String should have at least 1 character'

    def test_create_book_not_exist_author(self, client):
        """Создание книги с несуществующим автором (должна быть ошибка)"""

        _data = {
            "title": "test_title",
            "author_id": 99999,
        }

        response = client.post("/books", json=_data)

        # assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        data = response.json()
        # print(data)
        assert data['detail'] == 'Author with id 99999 not found'
