from django.urls import path
from ocr import views

app_name = "ocr"

urlpatterns = [
    path('', views.index, name="ocr"),
    path('process-image/', views.process_image, name="process-image")
]