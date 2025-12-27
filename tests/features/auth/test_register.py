from fastapi import status

class TestRegister:
    """Тесты для регистрации"""

    def test_register_success(self, client):
        """Успешная регистрация пользователя"""

        _data = {
            "username": "user",
            "email": "user1@gmail.com",
            "password": "password",
        }

        response = client.post("/auth/signup", json=_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        print(data)

        assert data["username"] == _data["username"]
        assert data["email"] == _data["email"]
        assert data["is_active"] is True
        assert data["email_verify_at"] is None
        assert "id" in data
        assert "password" not in data