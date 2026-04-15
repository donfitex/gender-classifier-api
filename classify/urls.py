from django.urls import path
from .views import classify_name, create_profile, list_profiles, get_profile, delete_profile


urlpatterns = [
    path('classify/', classify_name),
    path('profiles/', create_profile),
    path('profiles/', list_profiles),
    path('profiles/<uuid:id>/', get_profile),
    path('profiles/<uuid:id>/', delete_profile),
]