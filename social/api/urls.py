from django.urls import path, re_path, include
from .views import ChatAPIView, UserChatsAPIView, UserAPIView, MessageAPIView


urlpatterns = [
    path('userList', UserAPIView.as_view()),
    path('chatList', UserChatsAPIView.as_view()),
    path('chat', ChatAPIView.as_view()),
    path('messages', MessageAPIView.as_view()),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken'))
]
