from django.shortcuts import redirect
from rest_framework.response import Response
import os
import requests
from django.utils import timezone
from .models import User
from .utils import generate_tokens

#Github OAuth views
def github_login(request):
    client_id = os.getenv("GITHUB_CLIENT_ID")

    url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope=user"
    return redirect(url)

# Callback view to handle GitHub OAuth response
def github_callback(request):
    code = request.GET.get("code")

    token_res = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": os.getenv("GITHUB_CLIENT_ID"),
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
            "code": code,
        }
    ).json()

    access_token = token_res.get("access_token")

    user_res = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    user, _ = User.objects.get_or_create(
        github_id=user_res["id"],
        defaults={
            "username": user_res["login"],
            "avatar_url": user_res["avatar_url"]
        }
    )

    user.last_login_at = timezone.now()
    user.save()

    access, refresh = generate_tokens(user)

    return Response({
        "status": "success",
        "access_token": access,
        "refresh_token": refresh
    })