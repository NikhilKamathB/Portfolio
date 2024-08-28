import os
from hashlib import sha256
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from django.contrib import messages
from django.core.cache import cache
from django.http import JsonResponse
from django.core.exceptions import BadRequest
from home import CALENDAR_SERVICE
from home.validators import ChatResponse, CalendarData


def post_chat_view_handler(func):
    def wrapper(request, *args, **kwargs):
        if request.method == "POST":
            try:
                return func(request, *args, **kwargs)
            except BadRequest as e:
                return JsonResponse(
                    ChatResponse(success=False, message="Bad Request",
                                description=f"{e}").model_dump(),
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return JsonResponse(
                    ChatResponse(success=False, message="Internal Server Error",
                                description=f"{e}").model_dump(),
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return JsonResponse(
            ChatResponse(success=False, message="Method not allowed",
                        description="This method is not allowed.").model_dump(),
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    return wrapper

def cache_event_details_handler(func):
    def wrapper(request, *args, **kwargs):
        if not cache.get(settings.CACHE_EVENT_DETAILS, None):
            now = timezone.now()
            event_data = []
            this_month_start = now.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0)
            one_year_from_now = now + timezone.timedelta(days=settings.QUERY_DAYS)
            time_min = this_month_start.isoformat()
            time_max = one_year_from_now.isoformat()
            for calendar_id in settings.DEFAULT_CALENDAR_IDS:
                page_token = None
                while True:
                    events = CALENDAR_SERVICE.events().list(
                        calendarId=calendar_id,
                        timeMin=time_min,
                        timeMax=time_max,
                        pageToken=page_token,
                        singleEvents=True,
                    ).execute()
                    event_data.append(CalendarData(**events).model_dump_json())
                    page_token = events.get('nextPageToken')
                    if not page_token:
                        break
            cache.set(settings.CACHE_EVENT_DETAILS, event_data,
                    settings.CACHE_EVENT_DETAILS_EXPIRY)
        return func(request, *args, **kwargs)
    return wrapper

def authenticate_superuser_view_handler(func):
    def wrapper(request, *args, **kwargs):
        if request.method == "POST":
            passkey = request.POST.get("passkey").encode("utf-8")
            hash_object = sha256(passkey)
            sha_key = hash_object.hexdigest()
            if sha_key == os.getenv("PASSKEY", None):
                messages.add_message(request, messages.SUCCESS, "You are authenticated.")
                return func(request, show_event_summary=True, *args, **kwargs)
            else:
                messages.add_message(request, messages.WARNING, "You are not authenticated.")
        return func(request, show_event_summary=False, *args, **kwargs)
    return wrapper