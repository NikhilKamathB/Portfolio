import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect


def index(request):
    return render(request, "cm_mt/cm_mt.html", {"show_result": False})

def translate_text(request):
    if request.method == "POST":
        try:
            if request.session[settings.CMMT_SESSION_KEY_TRIES[0]] >= settings.CMMT_SESSION_KEY_TRIES[1]:
                messages.error(request, f"You have exceeded the maximum number of tries. Please try again later. This is to prevent abuse of the service and reduce the cost.")
            else:
                text = request.POST.get("cmmt-text")
                response = requests.post(settings.CM_MT_GCLOUD_RUN_API, json={"text": text}, timeout=None, headers={'Content-Type': 'application/json', 'Content-Length': str(len(text))})
                if response.status_code != 200:
                    messages.error(request, f"An error occurred: `{response.text}`. Please try again later.")
                    return redirect("cmmt:cmmt")
                if response.json()["success"] is False:
                    messages.error(request, f"{response.json()['error']}")
                    return redirect("cmmt:cmmt")
                messages.success(request, f"Code-mixed translation performed successfully!")
                response_json = response.json()
                response_json["show_result"] = True
                request.session[settings.CMMT_SESSION_KEY_TRIES[0]] += 1
                return render(request, "cm_mt/cm_mt.html", response_json)
        except Exception as e:
            messages.error(request, f"An error occurred: `{e}`. Please try again later.")
    return redirect("cmmt:cmmt")