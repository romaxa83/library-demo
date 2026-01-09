import time
from typing import Callable, Awaitable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.middlewares.requests_count import requests_count_middleware_dispatch
from loguru import logger
from src.config import config

type CallNext = Callable[[Request], Awaitable[Response]]


async def add_process_time_to_requests(
    request: Request,
    call_next: CallNext,
) -> Response:
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.5f}"
    return response


class ProcessTimeHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(self, *args, process_time_header_name: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.header_name = process_time_header_name

    async def dispatch(
        self,
        request: Request,
        call_next: CallNext,
    ) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers[self.header_name] = f"{process_time:.5f}"
        return response


def register_middlewares(app: FastAPI) -> None:
    @app.middleware("http")
    async def log_new_requests(
        request: Request,
        call_next: CallNext,
    ) -> Response:

        if not config.app.is_testing_env:
            logger.info(f"Request {request.method} to {request.url.path}")

        return await call_next(request)

    app.middleware("http")(add_process_time_to_requests)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors.allow_origins,
        allow_methods=config.cors.allow_methods,
        allow_headers=config.cors.allow_headers,
        allow_credentials=config.cors.allow_credentials,
        max_age=config.cors.max_age,
    )

    app.add_middleware(
        ProcessTimeHeaderMiddleware,
        process_time_header_name="X-Process-Time-New",
    )

    # добавление кастомного мидлевара
    app.add_middleware(
        BaseHTTPMiddleware,
        dispatch=requests_count_middleware_dispatch,
    )