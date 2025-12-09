from fastapi import HTTPException, status


class BookNotFoundError(HTTPException):
    def __init__(self, book_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )


class AuthorNotFoundError(HTTPException):
    def __init__(self, author_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id {author_id} not found"
        )
