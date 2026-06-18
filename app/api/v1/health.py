"""Простой эндпоинт проверки готовности."""

from fastapi import APIRouter


router = APIRouter(prefix='/health', tags=['Health'])
@router.get('')
async def health_check():
    # Делаем проверку максимально быстрой и без зависимостей.
    return {'status': 'OK!'}
