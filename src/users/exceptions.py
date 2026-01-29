from fastapi import HTTPException, status
from pydantic import EmailStr


class UserNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

class UserAlreadyExistsError(HTTPException):
    """Пользователь с таким email уже существует"""
    def __init__(self, email: str|EmailStr  ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{email}' already exists"
        )