from django.urls import path
from .views import github_login, github_callback_web, exchange_token, refresh_token, logout

urlpatterns = [
    path('auth/github', github_login),
    path('auth/github/callback/web', github_callback_web),
    path('auth/exchange', exchange_token),
    path("auth/refresh", refresh_token),
    path("auth/logout", logout),
]