from typing import Annotated
from fastapi import Depends

from src.database import DbSessionDep
from src.users.service import UserService

def get_user_service(session: DbSessionDep) -> UserService:
    return UserService(session)

# Type alias для удобства
UserServiceDep = Annotated[UserService, Depends(get_user_service)]