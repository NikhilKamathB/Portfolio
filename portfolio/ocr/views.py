import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect


def index(request):
    return render(request, "ocr/ocr.html", {"show_result": False})

def process_image(request):
    if request.method == "POST":
        try:
            response = requests.post(settings.OCR_GCLOUD_RUN_API, files=request.FILES, timeout=None)
            if response.status_code != 200:
                messages.error(request, f"An error occurred: `{response.text}`. Please try again later.")
                return redirect("ocr:ocr")
            if response.json()["success"] is False:
                messages.error(request, f"{response.json()['error']}")
                return redirect("ocr:ocr")
            if response.json()["special_message"] == "":
                messages.success(request, f"OCR performed successfully!")
            else:
                messages.success(request, f"{response.json()['special_message']}")
            response_json = response.json()
            response_json["show_result"] = True
            return render(request, "ocr/ocr.html", response_json)
        except Exception as e:
            messages.error(request, f"An error occurred: `{e}`. Please try again later.")
    return redirect("ocr:ocr")