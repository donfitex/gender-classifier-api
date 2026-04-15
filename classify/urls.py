from django.urls import path
from .views import classify_name, create_profile

urlpatterns = [
    path('classify/', classify_name),
    path('profiles/', create_profile),
]