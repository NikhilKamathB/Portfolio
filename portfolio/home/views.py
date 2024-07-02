from django.conf import settings
from rest_framework import status
from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import BadRequest


def index(request):
    return render(request, "home/home.html")

def chat(request):
    if request.method == "POST":
        try:
            query = request.POST.get("chat-query")
            if not query:
                raise BadRequest("You have not provided a query.")
            if not settings.CHAIN:
                raise BadRequest("Langchain is not initialized.")
            response_str = settings.CHAIN.invoke(query)
            return HttpResponse(response_str, status=status.HTTP_200_OK)
        except BadRequest as e:
            return HttpResponse(f"{e}", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return HttpResponse(f"An internal server error occurred! Sorry for this. You may contact Nikhil at `nikhilbo@kamath.work` if you need more help or get to know him.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HttpResponse("Method not allowed", status=status.HTTP_405_METHOD_NOT_ALLOWED)