import pytest
from fastapi import status

from src.rbac.permissions import Permissions


class TestUpdateRole:
    """Тесты для редактирования роли"""

    @pytest.mark.asyncio
    async def test_update_role_success(self, client, create_role, create_user, auth_header)->None:
        """Успешное обновление роли (без разрешений)"""
        user = await create_user(permissions=[Permissions.ROLE_UPDATE.value])
        header = await auth_header(user)

        model = await create_role(
            alias="moderator"
        )

        _update_data = {
            "alias": "moderator update"
        }

        response = await client.patch(f"/roles/{model.id}", json=_update_data, headers=header)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["id"] == model.id
        assert data["alias"] == _update_data["alias"]
        assert len(data["permissions"]) == 0

    @pytest.mark.asyncio
    async def test_update_role_success_with_perms(
        self,
        client,
        create_role,
        create_permission,
        create_user,
        auth_header
    ) -> None:
        """Успешное обновление роли"""
        user = await create_user(permissions=[Permissions.ROLE_UPDATE.value])
        header = await auth_header(user)

        perms_1 = await create_permission()
        perms_2 = await create_permission()

        model = await create_role(
            permissions=[perms_1.alias]
        )

        assert len(model.permissions) == 1

        _update_data = {
            "alias": model.alias,
            "permission_ids": [model.permissions[0].id, perms_2.id]
        }

        response = await client.patch(f"/roles/{model.id}", json=_update_data, headers=header)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["id"] == model.id
        assert len(data["permissions"]) == 2

    @pytest.mark.asyncio
    async def test_update_role_not_found(self, client, superadmin_headers)->None:
        """Попытка обновить несуществующую роль"""
        _update_data = {
            "alias": "title"
        }

        response = await client.patch("/roles/1", json=_update_data, headers=superadmin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Role with id [1] not found"


    @pytest.mark.asyncio
    async def test_not_perm(self, client, create_role, create_user, auth_header)->None:
        user = await create_user(permissions=[Permissions.BOOK_CREATE.value])
        header = await auth_header(user)

        model = await create_role()

        _update_data = {
            "alias": "Updated role"
        }

        response = await client.patch(f"/roles/{model.id}", json=_update_data, headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_not_auth(self, client, create_role)->None:
        model = await create_role()

        _update_data = {
            "alias": "Updated role"
        }

        response = await client.patch(f"/roles/{model.id}", json=_update_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED