import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock

from src.rbac.permissions import DefaultRole


class TestRegister:
    """Тесты для регистрации"""

    @pytest.mark.asyncio
    async def test_register_success(self, client, create_role):
        """Успешная регистрация пользователя"""

        # создаем дефолтную роль user
        await create_role(alias=DefaultRole.USER.value)

        _data = {
            "username": "user",
            "email": "user1@gmail.com",
            "password": "password",
        }

        response = await client.post("/auth/signup", json=_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["username"] == _data["username"]
        assert data["email"] == _data["email"]
        assert data["role"]['alias'] == DefaultRole.USER.value
        assert data["is_active"] is True
        assert data["email_verify_at"] is None
        assert "id" in data
        assert "password" not in data

    @pytest.mark.asyncio
    async def test_register_success_assert_send_email(self, client, create_role):
        """Успешная регистрация пользователя"""

        # создаем дефолтную роль user
        await create_role(alias=DefaultRole.USER.value)

        _data = {
            "username": "user",
            "email": "user1@gmail.com",
            "password": "password",
        }

        with patch('src.auth.service.send_verification_email', new_callable=AsyncMock) as mock_send_email:
            response = await client.post("/auth/signup", json=_data)

            assert response.status_code == status.HTTP_201_CREATED

            # Проверяем, что функция была вызвана один раз
            assert mock_send_email.call_count == 1

            # Проверяем, что функция вызвана с правильным email
            called_user = mock_send_email.call_args[0][0]
            assert called_user.email == _data["email"]

            # Проверяем, что второй аргумент - это токен (строка)
            verify_token = mock_send_email.call_args[0][1]
            assert isinstance(verify_token, str)
            assert len(verify_token) > 0

    @pytest.mark.asyncio
    async def test_fail_without_username(self, client, create_role):
        # создаем дефолтную роль user
        await create_role(alias=DefaultRole.USER.value)

        _data = {
            "email": "user1@gmail.com",
            "password": "password",
        }

        response = await client.post("/auth/signup", json=_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()

        assert data['detail'][0]['type'] == "missing"
        assert data['detail'][0]['loc'][1] == "username"
        assert data['detail'][0]['msg'] == "Field required"

    @pytest.mark.asyncio
    async def test_fail_without_email(self, client, create_role):
        # создаем дефолтную роль user
        await create_role(alias=DefaultRole.USER.value)

        _data = {
            "username": "user",
            "password": "password",
        }

        response = await client.post("/auth/signup", json=_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()

        assert data['detail'][0]['type'] == "missing"
        assert data['detail'][0]['loc'][1] == "email"
        assert data['detail'][0]['msg'] == "Field required"

    @pytest.mark.asyncio
    async def test_fail_not_valid_email(self, client, create_role):
        # создаем дефолтную роль user
        await create_role(alias=DefaultRole.USER.value)

        _data = {
            "username": "user",
            "email": "not_valid_email",
            "password": "password",
        }

        response = await client.post("/auth/signup", json=_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()

        assert data['detail'][0]['type'] == "value_error"
        assert data['detail'][0]['loc'][1] == "email"
        assert data['detail'][0]['msg'] == "value is not a valid email address: An email address must have an @-sign."

    @pytest.mark.asyncio
    async def test_fail_duplicate_email(self, client, create_role, create_user):
        # создаем дефолтную роль user
        await create_role(alias=DefaultRole.USER.value)

        _data = {
            "username": "user",
            "email": "user@gmail.com",
            "password": "password",
        }

        await create_user(email=_data["email"])

        response = await client.post("/auth/signup", json=_data)

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()

        assert data['detail'] ==f"User with email '{_data["email"]}' already exists"

    @pytest.mark.asyncio
    async def test_fail_without_password(self, client, create_role):
        # создаем дефолтную роль user
        await create_role(alias=DefaultRole.USER.value)

        _data = {
            "username": "user",
            "email": "user1@gmail.com",
        }

        response = await client.post("/auth/signup", json=_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()

        assert data['detail'][0]['type'] == "missing"
        assert data['detail'][0]['loc'][1] == "password"
        assert data['detail'][0]['msg'] == "Field required"

    @pytest.mark.asyncio
    async def test_fail_not_exist_default_role(self, client, create_role):
        _data = {
            "username": "user",
            "email": "user@gmail.com",
            "password": "password",
        }

        response = await client.post("/auth/signup", json=_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        assert data['detail'] == "Role with alias [user] not found"