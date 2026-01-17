from functools import lru_cache
from redis.asyncio import Redis
from src.config import config

@lru_cache
def get_redis() -> Redis:
    return Redis(
        host=config.redis.host,
        port=config.redis.port,
        # decode_responses=True # Раскомментируйте, если во всем проекте нужны строки вместо байтов
    )