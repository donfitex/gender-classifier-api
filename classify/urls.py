from django.urls import path
from .views import (
    classify_name,
    profiles,
    profile_detail,
)


urlpatterns = [
    path('classify/', classify_name),
    path('profiles/', profiles),
    path('profiles/<uuid:id>/', profile_detail),
]