import redis.asyncio as redis
import asyncio
from app.core.config import settings


async def get_connection():
    client = redis.Redis(host=settings.redis_host, port=settings.redis_port, password=settings.redis_password, db=settings.redis_db)
    await client.ping()
    return client
