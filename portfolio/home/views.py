
from markdown import markdown
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from django.contrib import messages
from django.shortcuts import render
from django.core.cache import cache
from django.http import JsonResponse
from django.core.exceptions import BadRequest
from home import AGENT
from home.validators import CalendarData, ChatResponse
from home.utils import send_email_utils, get_months_years, Calendar
from home.decorator import post_chat_view_handler, cache_event_details_handler, authenticate_superuser_view_handler


def index(request):
    return render(request, "home/home.html")

@cache_event_details_handler
@authenticate_superuser_view_handler
def schedule(request, show_event_summary: bool = False):
    now = timezone.now()
    event_data = list(map(lambda x: CalendarData.model_validate_json(x), cache.get(settings.CACHE_EVENT_DETAILS)))
    month = int(request.GET.get("month", now.month))
    year = int(request.GET.get("year", now.year))
    time_span = get_months_years()
    if (month, year) not in time_span:
        messages.warning(request, "The calendar for the requested month and year is not available.")
        month, year = now.month, now.year
    idx = time_span.index((month, year))
    prev_cal, next_cal = None, None
    if idx > 0:
        prev_cal = time_span[idx - 1]
    if idx < len(time_span) - 1:
        next_cal = time_span[idx + 1]
    cal = Calendar(year=year, month=month, calendar_data=event_data, show_event_summary=show_event_summary)
    context = {
        "calendar": cal.formatmonth(year, month),
        "prev_cal": prev_cal,
        "next_cal": next_cal
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