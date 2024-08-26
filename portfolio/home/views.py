
from markdown import markdown
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from django.shortcuts import render
from django.core.cache import cache
from django.http import JsonResponse
from django.core.exceptions import BadRequest
from django.views.decorators.cache import cache_page
from home.models import ChatResponse
from home import AGENT, CALENDAR_SERVICE
from home.validators import CalendarData
from home.decorator import post_chat_view_handler
from home.utils import send_email_utils, Calendar


def index(request):
    return render(request, "home/home.html")

# @cache_page(60 * 0.5)
def schedule(request):
    event_data = []
    now = timezone.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    one_year_from_now = now + timezone.timedelta(days=365)
    time_min = this_month_start.isoformat()
    time_max = one_year_from_now.isoformat()
    for calendar_id in settings.DEFAULT_CALENDAR_IDS:
        page_token = None
        while True:
            events = CALENDAR_SERVICE.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                pageToken=page_token
            ).execute()
            event_data.append(CalendarData(**events))
            page_token = events.get('nextPageToken')
            if not page_token: break
    cal = Calendar(year=now.year, month=now.month, calendar_data=event_data)
    context = {
        "calendar": cal.formatmonth(2024, 8)
    }
    return render(request, "home/schedule.html", context)

@post_chat_view_handler
def chat(request):
    query = request.POST.get("chat-query")
    if not query:
        raise BadRequest("You have not provided a query.")
    if not AGENT:
        raise BadRequest("Langchain is not initialized.")
    agent_response = AGENT.invoke({"question": query})
    response_raw = agent_response.get("output", "Sorry! I was unable to generate any respone. Contact Nikhil.")
    response_html = markdown(response_raw)
    if cache.get(settings.CHATBOT_MESSAGE_KEY) and settings.REGISTER_SEND_EMAIL_RETURN == response_raw:
        description = cache.get(settings.CHATBOT_MESSAGE_KEY)
        cache.delete(settings.CHATBOT_MESSAGE_KEY)
        return JsonResponse(
            ChatResponse(success=True, message=settings.REGISTER_SEND_EMAIL_RETURN,
                            description=description).model_dump(),
            status=status.HTTP_200_OK
        )
    return JsonResponse(
        ChatResponse(success=True, message="Success",
                        description=response_html).model_dump(),
        status=status.HTTP_200_OK
    )

@post_chat_view_handler
def send_email(request):
    message = request.POST.get("message")
    email = request.POST.get("email")
    if not message:
        raise BadRequest("You have not provided a message.")
    if not email:
        raise BadRequest("You have not provided an email.")
    send_email_utils(email, message)
    return JsonResponse(
        ChatResponse(success=True, message="Email sent",
                        description="Email sent successfully.").model_dump(),
        status=status.HTTP_200_OK
    )