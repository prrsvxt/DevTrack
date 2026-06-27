import smtplib
from email.message import EmailMessage

from app.core.config import settings


class EmailService:
    def send_message(self, to_email: str, subject: str, content: str) -> None:
        message = EmailMessage()

        message['From'] = settings.email_from
        message['To'] = to_email
        message['Subject'] = subject

        message.set_content(content)

        with smtplib.SMTP(host=settings.smtp_host, port=settings.smtp_port) as smtp:
            smtp.send_message(message)