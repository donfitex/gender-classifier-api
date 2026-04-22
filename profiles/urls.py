from django.urls import path
from .views import profiles, profile_detail, search_profiles

urlpatterns = [
    path('api/profiles', profiles),
    path('api/profiles/', profiles),
    path('api/search', search_profiles),
    path('api/profiles/<uuid:id>', profile_detail),
    path('api/profiles/<uuid:id>/', profile_detail),
]