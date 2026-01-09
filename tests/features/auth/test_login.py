import pytest
from fastapi import status

class TestLogin:
    """Тесты для логина"""

    @pytest.mark.asyncio
    async def test_login_success(self, client, create_user):
        """Успешный логин пользователя"""
        email = "test@gmail.com"
        password = "password"
        await create_user(email=email, password=password)

        _data = {
            "email": email,
            "password": password,
        }

        response = await client.post("/auth/login", json=_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["token_type"] == "Bearer"
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_wrong_email(self, client, create_user):
        email = "test@gmail.com"
        password = "password"
        await create_user(email=f"t{email}", password=password)

        _data = {
            "email": email,
            "password": password,
        }

        response = await client.post("/auth/login", json=_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        data = response.json()
        assert data["detail"] == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_wrong_password(self, client, create_user):
        email = "test@gmail.com"
        password = "password"
        await create_user(email=email, password=f"t{password}")

        _data = {
            "email": email,
            "password": password,
        }

        response = await client.post("/auth/login", json=_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        data = response.json()
        assert data["detail"] == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_without_password(self, client, create_user):
        email = "test@gmail.com"
        password = "password"
        await create_user(email=email, password=password)

        _data = {
            "email": email,
        }

        response = await client.post("/auth/login", json=_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_without_email(self, client, create_user):
        email = "test@gmail.com"
        password = "password"
        await create_user(email=email, password=password)

        _data = {
            "password": password,
        }

        response = await client.post("/auth/login", json=_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT