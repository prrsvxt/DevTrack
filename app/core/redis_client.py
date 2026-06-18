"""Фабрика Redis-подключения для lifespan-хука FastAPI."""

import redis.asyncio as redis
import asyncio
from app.core.config import settings


async def get_connection():
    # Падаем на старте сразу, если Redis недоступен.
    client = redis.Redis(host=settings.redis_host, port=settings.redis_port, password=settings.redis_password, db=settings.redis_db)
    await client.ping()
    return client
