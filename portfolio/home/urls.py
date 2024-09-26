from django.urls import path
from home import views

app_name = "home"

urlpatterns = [
    path('', views.index, name="home"),
    path('schedule/', views.schedule, name="schedule"),
    path('send-email/', views.send_email, name="send-email")
]