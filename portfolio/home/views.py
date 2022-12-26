from django.shortcuts import render
from home.models import *


def index(request):
    education = Education.objects.all().order_by("-start_date")
    work = Work.objects.all().order_by("-start_date")
    project = Project.objects.all().order_by("-start_date")
    context = {
        "education": education,
        "work": work,
        "project": project
    }
    return render(request, "home/home.html", context)