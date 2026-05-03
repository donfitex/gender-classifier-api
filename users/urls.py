from django.urls import path
from .views import github_callback, github_callback_web, github_login

urlpatterns = [
    path('auth/github', github_login),
    path('auth/github/callback', github_callback),
    path('auth/github/callback/web', github_callback_web),
]