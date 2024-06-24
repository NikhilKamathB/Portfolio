from rest_framework import status
from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, "home/home.html")

def chat(request):
    if request.method == "POST":
        chat_response = request.POST.get("chat-query")
        return HttpResponse(chat_response, status=status.HTTP_200_OK)
    return HttpResponse("error: method not allowed", status=status.HTTP_405_METHOD_NOT_ALLOWED)