from fastapi import status
import pytest
from pygments.lexers import data

from src.rbac.permissions import Permissions


class TestCreateRole:
    """Тесты для создания роли"""

    @pytest.mark.asyncio
    async def test_create_role_success_without_perm(self, client, create_user, auth_header)->None:
        """Успешное создание роли без прав"""
        user = await create_user(permissions=[Permissions.ROLE_CREATE.value])
        header = await auth_header(user)

        _data = {
            "alias": "moderator",
        }

        response = await client.post("/roles", json=_data, headers=header)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        print(data)
        assert "id" in data
        assert data["alias"] == _data["alias"]
        assert len(data["permissions"]) == 0

    @pytest.mark.asyncio
    async def test_create_role_success_with_perm(self, client, create_permission, create_user, auth_header) -> None:
        """Успешное создание роли с правами прав"""
        user = await create_user(permissions=[Permissions.ROLE_CREATE.value])
        header = await auth_header(user)

        perms_1 = await create_permission()
        perms_2 = await create_permission()

        _data = {
            "alias": "moderator",
            "permission_ids": [perms_1.id, perms_2.id],
        }

        response = await client.post("/roles", json=_data, headers=header)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        print(data)
        assert "id" in data
        assert data["alias"] == _data["alias"]
        assert len(data["permissions"]) == 2

    @pytest.mark.asyncio
    async def test_create_role_without_alias(self, client, create_author, superadmin_headers)->None:
        """Попытка создания роли без названия - должна быть ошибка"""

        _data = {}

        response = await client.post("/roles", json=_data, headers=superadmin_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_create_role_duplicate_alias(self, client, create_role, superadmin_headers)->None:
        """Создание роли с существующим названием (должна быть ошибка)"""
        role = await create_role()

        _data = {
            "title": role.alias,
        }

        response = await client.post("/roles", json=_data, headers=superadmin_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_not_perm(self, client, create_user, auth_header)->None:
        user = await create_user(permissions=[Permissions.ROLE_SHOW.value])
        header = await auth_header(user)

        _data = {
            "alias": "moderator",
        }

        response = await client.post("/roles", json=_data, headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_not_auth(self, client)->None:

        _data = {
            "alias": "moderator",
        }

        response = await client.post("/roles", json=_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED