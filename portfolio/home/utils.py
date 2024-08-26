from django.conf import settings
from calendar import HTMLCalendar
from django.core.mail import send_mail


def send_email_utils(email: str, message: str) -> None:
    """
    Send an email.
    """
    subject = settings.DEFAULT_EMAIL_SUBJECT
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email, settings.DEFAULT_NIKHIL_EMAIL])


class Calendar(HTMLCalendar):
    
    """
    Custom calendar class.
    """
    pass