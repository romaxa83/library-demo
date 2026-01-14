from typing import Annotated

from fastapi import status, Request, Depends
from redis.asyncio import Redis
from time import time
import random

class RateLimit:
    def __init__(self, redis: Redis):
        self._redis = redis

    async def is_limited(
        self,
        ip_address: str,
        endpoint: str,
        max_requests: int,
        window_seconds: int,
    )->bool:
        key = f"rate_limiter:{ip_address}:{endpoint}"

        current_ms = time() * 1000
        # получаем предел до которого записи актуальны (после они не актуальны и их можно удалять)
        window_start_ms = current_ms - window_seconds * 1000

        current_request = f"{current_ms}-{random.randint(0, 100_000)}"

        async with self._redis.pipeline() as pipe:
            # удаляем не актуальные значения
            await pipe.zremrangebyscore(key, 0, window_start_ms)

            # получаем сколько есть значений по ключу (после распаковки это второе значение, которое запишим в current_count)
            await pipe.zcard(key)

            # добавляем новое значение для этого запроса
            await pipe.zadd(key, {current_request: current_ms})

            # удаляем через определенной время старые записи (чтоб не забивать память не нужными данными)
            await pipe.expire(key, window_seconds)

            res = await pipe.execute()

        _, current_count, _, _ = res

        return current_count >= max_requests