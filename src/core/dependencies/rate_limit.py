from functools import lru_cache
from typing import Annotated
from fastapi import Request, Depends, HTTPException, status
from src.core.RateLimit import RateLimit
from .redis import get_redis

@lru_cache
def get_rate_limiter() -> RateLimit:
    return RateLimit(redis=get_redis())

# позволяет создавать для разных роутов свои rate-limit
def rate_limiter_factory(
    endpoint: str,
    max_requests: int,
    window_seconds: int,
):
    async def _rate_limiter(
        request: Request,
        rate_limiter: Annotated[RateLimit, Depends(get_rate_limiter)],
    ):
        ip_address = request.client.host

        limited = await rate_limiter.is_limited(
            ip_address=ip_address,
            endpoint=endpoint,
            max_requests=max_requests,
            window_seconds=window_seconds,
        )

        if limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

    return _rate_limiter