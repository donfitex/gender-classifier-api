from django.urls import path
from .views import profiles, profile_detail

urlpatterns = [
    path('api/profiles', profiles),
    path('api/profiles/', profiles),
    path('api/profiles/<uuid:id>', profile_detail),
    path('api/profiles/<uuid:id>/', profile_detail),
]