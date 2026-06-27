from celery import Celery

from app.core.config import settings


redis_url = (
    f"redis://:{settings.redis_password}"
    f"@{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
)

celery_app = Celery(
    "devtrack",
    broker=redis_url,
    backend=redis_url,
)


celery_app.conf.imports = ('app.tasks.email',)