from django.conf import settings
from rest_framework import status
from django.shortcuts import render
from django.core.cache import cache
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from home.models import *


def index(request):
    education = Education.objects.all().order_by("-start_date")
    work = Work.objects.all().order_by("-start_date")
    project = Project.objects.all().order_by('?')
    context = {
        "education": education,
        "work": work,
        "project": project
    }
    return render(request, "home/home.html", context)

@csrf_exempt
def chat(request):
    if request.method == "POST":
        if settings.CHATBOT_SESSION_KEY in cache:
            agent = cache.get(settings.CHATBOT_SESSION_KEY)
            try:
                if request.session[settings.CHATBOT_SESSION_KEY_TRIES[0]] >= settings.CHATBOT_SESSION_KEY_TRIES[1]:
                    return HttpResponse("error: too many tries.", status=status.HTTP_400_BAD_REQUEST)
                request.session[settings.CHATBOT_SESSION_KEY_TRIES[0]] += 1
                chat_response = agent.get_qa_agent_with_memory_chain().run(request.POST.get("chat-query"))
                return HttpResponse(chat_response, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return HttpResponse(f"An error occurred: `{e}`.\nYou may contact Nikhil @ nikhilbolakamath@gmail.com", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print("error: agent not found in cache.")
        return HttpResponse("error: agent not found in cache.", status=status.HTTP_404_NOT_FOUND)
    print("error: method not allowed.")
    return HttpResponse("error: method not allowed.", status=status.HTTP_405_METHOD_NOT_ALLOWED)