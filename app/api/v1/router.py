"""Версионированный роутер API, который собирает публичные endpoints."""

from fastapi import APIRouter


from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.team import team_router
from app.api.v1.team_member import team_member_router

api_router = APIRouter(prefix='/api/v1')
# Держим регистрацию роутов централизованной, чтобы точка входа была короткой.
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(tasks_router)
api_router.include_router(team_router)
api_router.include_router(team_member_router)
