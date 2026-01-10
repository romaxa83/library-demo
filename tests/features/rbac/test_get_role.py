import pytest
from fastapi import status

from src.rbac.permissions import Permissions, DefaultRole


class TestGetRole:
    """Тесты для получения роли"""

    @pytest.mark.asyncio
    async def test_get_role(self, client, create_role, create_permission, create_user, auth_header)->None:
        """Получить роль"""
        user = await create_user(permissions=[Permissions.ROLE_SHOW.value])
        header = await auth_header(user)

        perms = await create_permission()

        model = await create_role(
            permissions=[perms.alias]
        )

        response = await client.get(f"/roles/{model.id}", headers=header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == model.id
        assert data["alias"] == model.alias
        assert len(data["permissions"]) == 1
        assert data["permissions"][0]['alias'] == perms.alias

    @pytest.mark.asyncio
    async def test_get_role_no_exist(self, client, superadmin_headers)->None:
        """Получить не существующую роль"""
        response = await client.get("/roles/1", headers=superadmin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        assert data["detail"] == "Role with id [1] not found"

    @pytest.mark.asyncio
    async def test_get_role_as_superadmin(self, client, create_role, create_user, auth_header)->None:
        user = await create_user(permissions=[Permissions.ROLE_SHOW.value])
        header = await auth_header(user)

        model = await create_role(alias=DefaultRole.SUPERADMIN.value)

        response = await client.get(f"/roles/{model.id}", headers=header)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        assert data["detail"] == f"Role with id [{model.id}] not found"

    @pytest.mark.asyncio
    async def test_not_perm(self, client, create_user, auth_header)->None:
        user = await create_user(permissions=[Permissions.BOOK_LIST.value])
        header = await auth_header(user)

        response = await client.get(f"/roles/{user.role_id}", headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_not_auth(self, client, create_role)->None:
        model = await create_role()
        response = await client.get(f"/roles/{model.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED