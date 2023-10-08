from django.shortcuts import render


def index(request):
    return render(request, "acnn/acnn.html")