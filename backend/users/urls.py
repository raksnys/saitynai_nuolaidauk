from django.urls import path, include
from .views import ChangePasswordView, RegisterView, LoginView, UserListView, UserView, LogoutView, RefreshTokenView

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('change-password', ChangePasswordView.as_view()),
    path('logout', LogoutView.as_view()),
    path('refresh', RefreshTokenView.as_view(), name='refresh'),
    path('list', UserListView.as_view(), name='list-users'),
]