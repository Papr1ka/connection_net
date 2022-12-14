from django.urls import path, re_path, include
from .views import ChatAPIView, UserApiView, UserChatsAPIView, UserListAPIView, MessageAPIView, UserSearchApiView, UserGetApiView


urlpatterns = [
    path('userList', UserListAPIView.as_view()),
    path('chatList', UserChatsAPIView.as_view()),
    path('user', UserApiView.as_view()),
    path('user/search', UserSearchApiView.as_view()),
    path('user/<int:pk>/', UserGetApiView.as_view()),
    path('chat', ChatAPIView.as_view()),
    path('messages', MessageAPIView.as_view()),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken'))
]
