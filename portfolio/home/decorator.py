import os
from hashlib import sha256
from rest_framework import status
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import BadRequest
from home.validators import ChatResponse


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