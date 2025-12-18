from datetime import datetime
from fastapi import status


class TestGetBooks:
    """Тесты для получения списка книг"""

    def test_get_books_empty_list(self, client):
        """Получить пустой список книг"""
        response = client.get("/books")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["data"] == []
        assert data["meta"]["total"] == 0
        assert data["meta"]["count"] == 0
        assert data["meta"]["per_page"] == 10
        assert data["meta"]["current_page"] == 1
        assert data["meta"]["total_pages"] == 0
        assert data["meta"]["skip"] == 0

    def test_get_books_with_limit(self, client, create_books):
        """Получить книги, используя лимит"""

        create_books(count=3)

        response = client.get("/books?skip=0&limit=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # print(json.dumps(data, ensure_ascii=False, indent=2))
        assert len(data["data"]) == 2
        assert data["meta"]["total"] == 3
        assert data["meta"]["count"] == 2
        assert data["meta"]["per_page"] == 2
        assert data["meta"]["current_page"] == 1
        assert data["meta"]["total_pages"] == 2
        assert data["meta"]["skip"] == 0

    def test_get_books_with_skip(self, client, create_books):
        """Получить книги, используя skip"""

        create_books(3)

        response = client.get("/books?skip=2&limit=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["data"]) == 1
        assert data["meta"]["total"] == 3
        assert data["meta"]["count"] == 1
        assert data["meta"]["per_page"] == 2
        assert data["meta"]["current_page"] == 2
        assert data["meta"]["total_pages"] == 2
        assert data["meta"]["skip"] == 2

    def test_get_book_with_search(self, client, create_book):
        """Получить книгу с поиском по названию"""

        title = "Good book"
        model = create_book(title=title)
        create_book(title="Tester")

        response = client.get("/books?search=book")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["title"] == model.title
        assert data["meta"]["total"] == 1

    def test_get_book_with_author_id(self, client, create_book, create_author):
        """Получить книги по автору"""

        author = create_author()
        create_book(author=author)
        create_book(author=author)
        create_book(title="Tester")

        response = client.get(f"/books?author_id={author.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # print(json.dumps(data, ensure_ascii=False, indent=2))
        assert len(data["data"]) == 2
        assert data["data"][0]["author_id"] == author.id
        assert data["data"][1]["author_id"] == author.id

    def test_get_book_with_is_available_as_true(self, client, create_book):
        """Получить книги по наличию"""

        create_book(is_available=True)
        create_book(is_available=False)
        create_book(is_available=False)

        response = client.get(f"/books?is_available=True")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1

    def test_get_book_with_is_available_as_false(self, client, create_book):
        """Получить книги по наличию"""

        create_book(is_available=True)
        create_book(is_available=False)
        create_book(is_available=False)

        response = client.get(f"/books?is_available=False")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2

    def test_get_book_with_is_available_as_all(self, client, create_book):
        """Получить книги по наличию"""

        create_book(is_available=True)
        create_book(is_available=False)
        create_book(is_available=False)

        response = client.get(f"/books")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 3

    def test_get_books_with_only_active(self, client, create_book):
        """Получить книг только активных (не удаленных)"""

        model = create_book()
        create_book(deleted_at=datetime.now())

        response = client.get("/books")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == model.id

    def test_get_books_with_only_deleted(self, client, create_book):
        """Получить книги только удаленные"""

        create_book()
        deleted_model = create_book(deleted_at=datetime.now())

        response = client.get("/books?deleted=deleted")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == deleted_model.id

    def test_get_books_with_all_status(self, client, create_book):
        """Получить книги и активных и удаленных"""

        create_book()
        create_book(deleted_at=datetime.now())

        response = client.get("/books?deleted=all")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2

    def test_get_books_with_sort_asc_as_title(self, client, create_book):
        """Получить авторов с сортировкой по названию"""

        model_1 = create_book(title="Tom")
        model_2 = create_book(title="Alen")
        model_3 = create_book(title="John")

        response = client.get("/books?sort_by=title&sort_order=asc")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 3
        assert data["data"][0]["title"] == model_2.title
        assert data["data"][1]["title"] == model_3.title
        assert data["data"][2]["title"] == model_1.title

    def test_get_books_with_sort_desc_as_title(self, client, create_book):
        """Получить авторов с сортировкой по названию"""

        model_1 = create_book(title="Tom")
        model_2 = create_book(title="Alen")
        model_3 = create_book(title="John")

        response = client.get("/books?sort_by=title&sort_order=desc")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 3
        assert data["data"][0]["title"] == model_1.title
        assert data["data"][1]["title"] == model_3.title
        assert data["data"][2]["title"] == model_2.title

    def test_get_books_with_sort_asc_as_page(self, client, create_book):
        """Получить авторов с сортировкой по кол-ву страниц"""

        model_1 = create_book(page=3)
        model_2 = create_book(page=46)
        model_3 = create_book(page=17)

        response = client.get("/books?sort_by=page&sort_order=asc")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 3
        assert data["data"][0]["title"] == model_1.title
        assert data["data"][1]["title"] == model_3.title
        assert data["data"][2]["title"] == model_2.title

    def test_get_books_with_sort_desc_as_page(self, client, create_book):
        """Получить авторов с сортировкой по кол-ву страниц"""

        model_1 = create_book(page=3)
        model_2 = create_book(page=46)
        model_3 = create_book(page=17)

        response = client.get("/books?sort_by=page&sort_order=desc")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 3
        assert data["data"][0]["title"] == model_2.title
        assert data["data"][1]["title"] == model_3.title
        assert data["data"][2]["title"] == model_1.title