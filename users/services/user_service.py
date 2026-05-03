from ..models import User
from django.utils import timezone


def create_or_update_user(data):
    github_id = str(data.get("id"))

    user, _ = User.objects.update_or_create(
        github_id=github_id,
        defaults={
            "username": data.get("login"),
            "email": data.get("email"),
            "avatar_url": data.get("avatar_url"),
            "last_login_at": timezone.now(),
        }
    )

    return user