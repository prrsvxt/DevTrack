from smtplib import (
    SMTPConnectError,
    SMTPDataError,
    SMTPHeloError,
    SMTPServerDisconnected,
)

from app.core.celery_app import celery_app
from app.services.email_service import EmailService
from app.emails.no_reply_messages import send_welcome_email


@celery_app.task(bind=True, max_retries=3)
def task_welcome_email(self, email: str) -> None:
    email_service = EmailService()

    try:
        send_welcome_email(email_service, email)
    except (
        SMTPConnectError,
        SMTPServerDisconnected,
        SMTPHeloError,
        SMTPDataError,
        TimeoutError,
        ConnectionError,
        OSError,
    ) as exc:
        raise self.retry(exc=exc, countdown=3)
