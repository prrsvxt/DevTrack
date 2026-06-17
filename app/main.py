from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis.asyncio as redis

from app.api.v1.router import api_router
from app.core.config import settings
from app.core import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client_ = await redis_client.get_connection()
    app.state.redis = redis_client_
    print('redis connected')
    yield
    await app.state.redis.aclose()
    print('redis disconnected')

app = FastAPI(title='DevTrack API', version='0.1.0', lifespan=lifespan)
app.include_router(api_router)
