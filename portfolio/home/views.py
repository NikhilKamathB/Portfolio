from django.conf import settings
from rest_framework import status
from django.shortcuts import render
from django.core.cache import cache
from django.http import HttpResponse
from home.models import *


def index(request):
    return render(request, "home/home.html")

def chat(request):
    if request.method == "POST":
        if settings.CHATBOT_SESSION_KEY in cache:
            agent = cache.get(settings.CHATBOT_SESSION_KEY)
            try:
                if request.session[settings.CHATBOT_SESSION_KEY_TRIES[0]] >= settings.CHATBOT_SESSION_KEY_TRIES[1]:
                    return HttpResponse("error: too many tries.", status=status.HTTP_400_BAD_REQUEST)
                request.session[settings.CHATBOT_SESSION_KEY_TRIES[0]] += 1
                chat_response = agent.get_qa_agent_with_memory_chain().run(input=request.POST.get("chat-query"))
                return HttpResponse(chat_response, status=status.HTTP_200_OK)
            except ValueError as ve:
                response = str(ve)
                if str(ve).startswith("Could not parse LLM output: "):
                    return HttpResponse(response[len("Could not parse LLM output: "):], status=status.HTTP_200_OK)
                return HttpResponse(f"An error occurred: `{ve}`.\nYou may contact Nikhil @ nikhilbolakamath@gmail.com", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return HttpResponse(f"An error occurred: `{e}`.\nYou may contact Nikhil @ nikhilbolakamath@gmail.com", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return HttpResponse("error: agent not found in cache.", status=status.HTTP_404_NOT_FOUND)
    return HttpResponse("error: method not allowed.", status=status.HTTP_405_METHOD_NOT_ALLOWED)