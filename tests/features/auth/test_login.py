from fastapi import status


class TestLogin:
    """Тесты для логина"""

    def test_login_success(self, client, create_user):
        """Успешный логин пользователя"""
        email = "test@gmail.com"
        password = "password"
        model = create_user(email=email, password=password)

        _data = {
            "email": email,
            "password": password,
        }

        response = client.post("/auth/login", json=_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["token_type"] == "Bearer"
        assert "access_token" in data
        assert "refresh_token" in data