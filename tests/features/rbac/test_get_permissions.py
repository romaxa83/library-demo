import pytest
from fastapi import status

from src.rbac.permissions import Permissions


class TestGetPermissions:
    """Тесты для получения списка разрешений"""

    @pytest.mark.asyncio
    async def test_get_perm_list(self, client, create_user, auth_header)->None:
        """Получить список разрешений"""
        user = await create_user(permissions=[Permissions.PERMISSION_LIST.value])
        header = await auth_header(user)

        response = await client.get("/permissions", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_get_some_permissions(self, client, create_permission, superadmin_headers) -> None:
        await create_permission()
        await create_permission()
        await create_permission()

        response = await client.get("/permissions", headers=superadmin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["data"]) == 3

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

        response = await client.get("/permissions", headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_not_auth(self, client)->None:
        response = await client.get("/permissions")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED