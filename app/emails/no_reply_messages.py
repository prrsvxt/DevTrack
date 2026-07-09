from app.services.email_service import EmailService


def send_welcome_email(email_service: EmailService, to_email: str) -> None:
    subject = "Welcome to DevTrack"
    content = "Welcome to DevTrack! \n\nRegistration has been passed successfully!"

    email_service.send_message(to_email, subject, content)
