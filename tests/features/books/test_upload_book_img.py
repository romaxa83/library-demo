import pytest
from io import BytesIO
from fastapi import status
from unittest.mock import patch, AsyncMock
from src.rbac.permissions import Permissions


class TestUploadBookImage:
    """Тесты для загрузки изображений книг"""

    @pytest.mark.asyncio
    async def test_upload_image_success(self, client, create_book, create_user, auth_header, create_test_image):
        """Успешная загрузка изображения"""
        user = await create_user(permissions=[Permissions.BOOK_UPLOAD_IMG.value])
        header = await auth_header(user)

        book = await create_book()

        # Создаем фейковый файл в памяти
        image_file = create_test_image()
        files = {"file": ("test.jpg", image_file, "image/jpeg")}

        # Мокируем метод save бэкенда хранилища, чтобы не писать на диск
        with patch("src.media.storage.LocalStorageBackend.save", new_callable=AsyncMock) as mock_save:
            mock_save.return_value = "fake/path/test.jpg"

            response = await client.post(
                f"/books/{book.id}/upload-img",
                files=files,
                headers=header
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Проверяем, что в ответе есть картинки
            assert len(data["images"]) > 0
            assert data["images"][0]["filename"] == "test.jpg"

            # Проверяем, что физическое сохранение вызывалось (оригинал + превью)
            # Если у вас 2 превью (small, medium), то вызовов будет 3
            assert mock_save.call_count == 3

    @pytest.mark.asyncio
    async def test_upload_image_invalid_type(self, client, create_book, superadmin_headers):
        """Попытка загрузки файла недопустимого типа"""
        book = await create_book()

        # Передаем текстовый контент вместо картинки
        file_content = b"this is not an image"
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}

        response = await client.post(
            f"/books/{book.id}/upload-img",
            files=files,
            headers=superadmin_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Неподдерживаемый тип файла" in response.json()["detail"]


    @pytest.mark.asyncio
    async def test_upload_image_too_large(self, client, create_book, superadmin_headers):
        """Попытка загрузки слишком большого файла"""
        book = await create_book()

        # Создаем контент больше 5MB (забиваем байтами)
        large_content = b"0" * (6 * 1024 * 1024)
        files = {"file": ("large.jpg", BytesIO(large_content), "image/jpeg")}

        response = await client.post(
            f"/books/{book.id}/upload-img",
            files=files,
            headers=superadmin_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Файл слишком большой" in response.json()["detail"]


    @pytest.mark.asyncio
    async def test_upload_image_no_permission(self, client, create_book, create_user, auth_header, create_test_image):
        """Попытка загрузки без прав (BOOK_DELETE требуется по вашему роуту)"""
        book = await create_book()
        user = await create_user(permissions=[Permissions.BOOK_SHOW.value])
        header = await auth_header(user)

        # Создаем фейковый файл в памяти
        image_file = create_test_image()
        files = {"file": ("test.jpg", image_file, "image/jpeg")}

        response = await client.post(
            f"/books/{book.id}/upload-img",
            files=files,
            headers=header
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_upload_image_no_auth(self, client, create_book, create_test_image):
        """Попытка загрузки без прав (BOOK_DELETE требуется по вашему роуту)"""
        book = await create_book()

        # Создаем фейковый файл в памяти
        image_file = create_test_image()
        files = {"file": ("test.jpg", image_file, "image/jpeg")}

        response = await client.post(
            f"/books/{book.id}/upload-img",
            files=files
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED