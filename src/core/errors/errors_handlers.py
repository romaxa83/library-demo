from fastapi import FastAPI, Request, status
from sqlalchemy.exc import DatabaseError
from pydantic import ValidationError
from fastapi.responses import ORJSONResponse
from starlette.responses import JSONResponse

from src.core.schemas.responses import ErrorResponse


def register_errors_handlers(app: FastAPI) -> None:


    # @app.exception_handler(ValidationError)
    # def handle_py_validation_error(
    #         request: Request,
    #         exception: ValidationError
    # ):
    #     print('==============')
    #     print(exception)
    #     return exception

    @app.exception_handler(DatabaseError)
    def handle_db_error(
            request: Request,
            exc: ValidationError,
    ) -> ORJSONResponse:

        # msg = "An unexpected error has occurred. Our admins are already working on it."
        msg = (exc.orig.args)

        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"msg": msg},
        )

    @app.exception_handler(ValueError)
    def handle_value_error(
            request: Request,
            exc: ValueError,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"msg": exc},
        )