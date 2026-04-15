from django.urls import path
from .views import classify_name, profiles, get_profile, delete_profile


urlpatterns = [
    path('classify/', classify_name),
    path('profiles/', profiles),
    path('profiles/<uuid:id>/', get_profile),
    path('profiles/<uuid:id>/', delete_profile),
]