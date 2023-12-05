from django.urls import path
from cm_mt import views

app_name = "cmmt"

urlpatterns = [
    path('', views.index, name="cmmt"),
    path('translate-text/', views.translate_text, name="translate-text")
]