import pytest
from faker import Faker
from PIL import Image
import io


@pytest.fixture(scope="session")
def fake():
    """Фикстура для генерации фейковых данных"""
    return Faker()

@pytest.fixture
def create_test_image():
    """Создает валидное изображение в памяти для тестов"""
    def _create(filename="test.jpg", size=(100, 100), color="red"):
        file = io.BytesIO()
        image = Image.new("RGB", size, color)
        image.save(file, "JPEG")
        file.name = filename
        file.seek(0)
        return file
    return _create