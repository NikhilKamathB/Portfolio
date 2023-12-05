from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ImproperlyConfigured


class CmmtMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if not hasattr(request, "session"):
            raise ImproperlyConfigured(
                "The Django cmmt middleware requires session "
                "middleware to be installed. Edit your MIDDLEWARE setting to "
                "insert "
                "'django.contrib.sessions.middleware.SessionMiddleware' before "
                "'django.contrib.auth.middleware.AuthenticationMiddleware'."
            )
        if settings.CMMT_SESSION_KEY_TRIES[0] not in request.session:
            request.session[settings.CMMT_SESSION_KEY_TRIES[0]] = 0