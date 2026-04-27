from uuid6 import uuid7
from django.db import models

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)

    github_id = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    avatar_url = models.URLField(null=True, blank=True)

    role = models.CharField(
        max_length=20,
        choices=[("admin", "Admin"), ("analyst", "Analyst")],
        default="analyst"
    )

    is_active = models.BooleanField(default=True)

    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

#Token model to store refresh tokens for users
class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)