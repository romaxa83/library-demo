import pytest
from fastapi import status

from src.rbac.permissions import Permissions, DefaultRole


class TestDeleteRole:
    """Тесты для удаления роли"""

    @pytest.mark.asyncio
    async def test_delete_role_success(self, client, create_role, create_user, auth_header)->None:
        """Успешное полное удаление автора"""
        user = await create_user(permissions=[
            Permissions.ROLE_LIST.value,
            Permissions.ROLE_DELETE.value
        ])
        header = await auth_header(user)

        model = await create_role()

        # смотрим что роль есть
        response = await client.get("/roles", headers=header)
        data = response.json()

        assert len(data["data"]) == 2

        # удаляем
        response = await client.delete(f"/roles/{model.id}", headers=header)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # смотрим что роли нет
        response = await client.get("/roles", headers=header)
        data = response.json()
        assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_delete_nonexistent_role(self, client, superadmin_user, auth_header)->None:
        header = await auth_header(superadmin_user)

        response = await client.delete("/roles/99999", headers=header)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_superadmin_role(self, client, create_role, create_user, auth_header)->None:
        user = await create_user(permissions=[
            Permissions.ROLE_LIST.value,
            Permissions.ROLE_DELETE.value
        ])
        header = await auth_header(user)

        model = await create_role(alias=DefaultRole.SUPERADMIN.value)

        response = await client.delete(f"/roles/{model.id}", headers=header)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_default_role(self, client, create_role, create_user, superadmin_headers) -> None:
        model = await create_role(alias=DefaultRole.USER.value)

        response = await client.delete(f"/roles/{model.id}", headers=superadmin_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data = response.json()
        assert data["detail"] == 'Role can not be deleted'

    @pytest.mark.asyncio
    async def test_delete_role_as_attach_user(self, client, create_role, create_user, superadmin_headers) -> None:
        model = await create_role()
        await create_user(role_alias=model.alias)
        response = await client.delete(f"/roles/{model.id}", headers=superadmin_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data = response.json()
        assert data["detail"] == "Cannot delete role because it is assigned to one or more users"

    @pytest.mark.asyncio
    async def test_not_perm(self, client, create_role, create_user, auth_header)->None:
        user = await create_user(permissions=[
            Permissions.AUTHOR_LIST.value
        ])
        header = await auth_header(user)

        model = await create_role()

        # удаляем
        response = await client.delete(f"/roles/{model.id}", headers=header)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_not_auth(self, client, create_role)->None:
        model = await create_role()

        # удаляем
        response = await client.delete(f"/roles/{model.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED