from enum import Enum

class DefaultRole(Enum):
    USER       = "user"
    SUPERADMIN = "superadmin"

class PermissionGroup(Enum):
    USER       = "user"
    ROLE       = "role"
    AUTHOR     = "author"
    BOOK       = "book"
    PERMISSION = "permission"
    MEDIA      = "media"

class  Permissions(Enum):
    # Action by user
    USER_SHOW   = f"{PermissionGroup.USER.value}.show"
    USER_LIST   = f"{PermissionGroup.USER.value}.list"
    USER_CREATE = f"{PermissionGroup.USER.value}.create"
    USER_UPDATE = f"{PermissionGroup.USER.value}.update"
    USER_DELETE = f"{PermissionGroup.USER.value}.delete"

    # Action by role
    ROLE_SHOW       = f"{PermissionGroup.ROLE.value}.show"
    ROLE_LIST       = f"{PermissionGroup.ROLE.value}.list"
    ROLE_CREATE     = f"{PermissionGroup.ROLE.value}.create"
    ROLE_UPDATE     = f"{PermissionGroup.ROLE.value}.update"
    ROLE_DELETE     = f"{PermissionGroup.ROLE.value}.delete"
    PERMISSION_LIST = f"{PermissionGroup.PERMISSION.value}.list"

    # Action by author
    AUTHOR_SHOW         = f"{PermissionGroup.AUTHOR.value}.show"
    AUTHOR_LIST         = f"{PermissionGroup.AUTHOR.value}.list"
    AUTHOR_CREATE       = f"{PermissionGroup.AUTHOR.value}.create"
    AUTHOR_UPDATE       = f"{PermissionGroup.AUTHOR.value}.update"
    AUTHOR_DELETE       = f"{PermissionGroup.AUTHOR.value}.delete"
    AUTHOR_RESTORE      = f"{PermissionGroup.AUTHOR.value}.restore"
    AUTHOR_FORCE_DELETE = f"{PermissionGroup.AUTHOR.value}.force_delete"

    # Action by book
    BOOK_SHOW       = f"{PermissionGroup.BOOK.value}.show"
    BOOK_LIST       = f"{PermissionGroup.BOOK.value}.list"
    BOOK_CREATE     = f"{PermissionGroup.BOOK.value}.create"
    BOOK_UPDATE     = f"{PermissionGroup.BOOK.value}.update"
    BOOK_DELETE     = f"{PermissionGroup.BOOK.value}.delete"
    BOOK_UPLOAD_IMG = f"{PermissionGroup.BOOK.value}.upload_img"

    MEDIA_DELETE = f"{PermissionGroup.MEDIA.value}.delete"


def get_permissions_for_seed():
    return {
        PermissionGroup.USER.value: [
            {"alias": Permissions.USER_SHOW.value, "description": "Просмотр пользователя"},
            {"alias": Permissions.USER_LIST.value, "description": "Просмотр пользователей"},
            {"alias": Permissions.USER_CREATE.value, "description": "Создать пользователя"},
            {"alias": Permissions.USER_UPDATE.value, "description": "Редактировать пользователя"},
            {"alias": Permissions.USER_DELETE.value, "description": "Удалить пользователя"},
        ],
        PermissionGroup.ROLE.value: [
            {"alias": Permissions.ROLE_SHOW.value, "description": "Просмотр роли"},
            {"alias": Permissions.ROLE_LIST.value, "description": "Просмотр ролей"},
            {"alias": Permissions.ROLE_CREATE.value, "description": "Создать роль"},
            {"alias": Permissions.ROLE_UPDATE.value, "description": "Редактировать роль"},
            {"alias": Permissions.ROLE_DELETE.value, "description": "Удалить роль"},
        ],
        PermissionGroup.PERMISSION.value: [
            {"alias": Permissions.PERMISSION_LIST.value, "description": "Просмотр разрешений"},
        ],
        PermissionGroup.AUTHOR.value: [
            {"alias": Permissions.AUTHOR_SHOW.value, "description": "Просмотр автора"},
            {"alias": Permissions.AUTHOR_LIST.value, "description": "Просмотр авторов"},
            {"alias": Permissions.AUTHOR_CREATE.value, "description": "Создать автора"},
            {"alias": Permissions.AUTHOR_UPDATE.value, "description": "Редактировать автора"},
            {"alias": Permissions.AUTHOR_DELETE.value, "description": "Удалить автора (мягкое удаление)"},
            {"alias": Permissions.AUTHOR_RESTORE.value, "description": "Восстановить автора"},
            {"alias": Permissions.AUTHOR_FORCE_DELETE.value, "description": "Удалить автора (жесткое удаление)"},
        ],
        PermissionGroup.BOOK.value: [
            {"alias": Permissions.BOOK_SHOW.value, "description": "Просмотр книги"},
            {"alias": Permissions.BOOK_LIST.value, "description": "Просмотр книг"},
            {"alias": Permissions.BOOK_CREATE.value, "description": "Создать книгу"},
            {"alias": Permissions.BOOK_UPDATE.value, "description": "Редактировать книгу"},
            {"alias": Permissions.BOOK_DELETE.value, "description": "Удалить книгу"},
            {"alias": Permissions.BOOK_UPLOAD_IMG.value, "description": "Загрузить картинок для книг"},
        ],
        PermissionGroup.MEDIA.value: [
            {"alias": Permissions.MEDIA_DELETE.value, "description": "Удалить файл"},
        ],
    }

def get_permissions_for_roles():
    return {
        DefaultRole.USER.value: [
            Permissions.AUTHOR_SHOW.value,
            Permissions.AUTHOR_LIST.value,
            Permissions.BOOK_SHOW.value,
            Permissions.BOOK_LIST.value
        ],
    }
