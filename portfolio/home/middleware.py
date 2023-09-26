from django.conf import settings
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ImproperlyConfigured
from home.agent import Agent


class ChatbotMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if not hasattr(request, "session"):
            raise ImproperlyConfigured(
                "The Django chatbot middleware requires session "
                "middleware to be installed. Edit your MIDDLEWARE setting to "
                "insert "
                "'django.contrib.sessions.middleware.SessionMiddleware' before "
                "'django.contrib.auth.middleware.AuthenticationMiddleware'."
            )
        if not settings.CHATBOT_SESSION_KEY in cache:
            cache.set(settings.CHATBOT_SESSION_KEY, Agent())
        if settings.CHATBOT_SESSION_KEY_TRIES[0] not in request.session:
            request.session[settings.CHATBOT_SESSION_KEY_TRIES[0]] = 0