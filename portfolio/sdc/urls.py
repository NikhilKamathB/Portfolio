from django.urls import path
from sdc import views

app_name = "sdc"

urlpatterns = [
    path('', views.index, name="sdc")
]