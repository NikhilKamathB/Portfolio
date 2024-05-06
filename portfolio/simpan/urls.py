from django.urls import path
from simpan import views

app_name = "simpan"

urlpatterns = [
    path('', views.index, name="simpan")
]
