from django.urls import path

from .views import ChatAPI

app_name = "chat"

urlpatterns = [
    path('<int:receiver_id>/', ChatAPI.as_view(), name='chat_api'),
]
