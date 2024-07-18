from django.conf import settings


def send_email_utils(email: str, message: str) -> None:
    """
    Send an email to Nikhil
    """
    print(f"Sending email to Nikhil {settings.DEFAULT_NIKHIL_EMAIL} and person with email {email} with message {message}")