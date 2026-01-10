import pytest
from fastapi import status

from src.rbac.permissions import Permissions, DefaultRole


class TestGetRoles:
    """Тесты для получения списка ролей"""

    @pytest.mark.asyncio
    async def test_get_role_list(self, client, create_user, auth_header)->None:
        """Получить пустой список ролей"""
        user = await create_user(permissions=[Permissions.ROLE_LIST.value])
        header = await auth_header(user)

        response = await client.get("/roles", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == user.role_id

    @pytest.mark.asyncio
    async def test_get_roles_list_without_superadmin(self, client, create_role, create_user, auth_header) -> None:
        """Получить пустой список ролей"""
        user = await create_user(permissions=[Permissions.ROLE_LIST.value])
        header = await auth_header(user)

        await create_role(alias=DefaultRole.SUPERADMIN.value)

        response = await client.get("/roles", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == user.role_id

    @pytest.mark.asyncio
    async def test_get_roles_list_some_roles(self, client, create_role, create_user, auth_header) -> None:
        """Получить пустой список ролей"""
        user = await create_user(permissions=[Permissions.ROLE_LIST.value])
        header = await auth_header(user)

        await create_role()
        await create_role()

        response = await client.get("/roles", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["data"]) == 3

    @pytest.mark.asyncio
    async def test_not_perm(self, client, create_user, auth_header)->None:
        user = await create_user(permissions=[Permissions.ROLE_SHOW.value])
        header = await auth_header(user)

        response = await client.get("/roles", headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_not_auth(self, client)->None:
        response = await client.get("/books")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED