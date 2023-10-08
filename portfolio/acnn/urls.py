from django.urls import path
from acnn import views

app_name = "acnn"

urlpatterns = [
    path('', views.index, name="acnn")
]