from app.emails.no_reply_messages import send_welcome_email


class FakeEmailService:
    def __init__(self):
        self.sent_messages = []

    def send_message(self, to_email: str, subject: str, content: str) -> None:
        self.sent_messages.append(
            {"to_email": to_email, "subject": subject, "content": content}
        )


def test_send_welcome_email():
    fake_email_service = FakeEmailService()

    send_welcome_email(email_service=fake_email_service, to_email="test@example.com")

    assert len(fake_email_service.sent_messages) == 1

    sent_message = fake_email_service.sent_messages[0]

    assert sent_message["to_email"] == "test@example.com"
    assert sent_message["subject"] == "Welcome to DevTrack"
    assert "Welcome to DevTrack" in sent_message["content"]
