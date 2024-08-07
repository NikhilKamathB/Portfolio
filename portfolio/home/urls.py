from django.urls import path
from home import views

app_name = "home"

urlpatterns = [
    path('', views.index, name="home"),
    path('chat/', views.chat, name="chat"),
    path('send-email/', views.send_email, name="send-email")
]