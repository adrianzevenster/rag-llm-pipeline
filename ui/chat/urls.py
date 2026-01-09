from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.chat_page, name="chat_page"),
    path("api/chat", views.chat_api, name="chat_api"),
    path("health", views.health_page, name="health_page"),
]
