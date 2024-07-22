
from django.conf import settings
from rest_framework import status
from django.shortcuts import render
from django.core.cache import cache
from django.http import JsonResponse
from django.core.exceptions import BadRequest
from home import AGENT
from home.models import ChatResponse
from home.utils import send_email_utils
from home.decorator import post_view_handler


def index(request):
    return render(request, "home/home.html")

@post_view_handler
def chat(request):
    query = request.POST.get("chat-query")
    if not query:
        raise BadRequest("You have not provided a query.")
    if not AGENT:
        raise BadRequest("Langchain is not initialized.")
    agent_response = AGENT.invoke({"question": query})
    response_str = agent_response.get("output", "Sorry! I was unable to generate any respone. Contact Nikhil.")
    if cache.get("chatbot_message") and response_str == settings.REGISTER_SEND_EMAIL_RETURN:
        description = cache.get("chatbot_message")
        cache.delete("chatbot_message")
        return JsonResponse(
            ChatResponse(success=True, message=response_str,
                            description=description).model_dump(),
            status=status.HTTP_200_OK
        )
    return JsonResponse(
        ChatResponse(success=True, message="Success",
                        description=response_str).model_dump(),
        status=status.HTTP_200_OK
    )

@post_view_handler
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