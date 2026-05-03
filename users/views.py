from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
import secrets
import requests
from django.utils import timezone
from .models import User
from .utils import web_generate_tokens

from .services.github_service import (
    exchange_code_for_token,
    get_github_user
)

from .services.user_service import create_or_update_user
from .services.token_services import generate_tokens

from django.http import JsonResponse
from .services.oauth_service import build_github_url

STATE_STORE = set()

#Github OAuth views
def github_login(request):
    state = secrets.token_urlsafe(16)
    code_challenge = request.GET.get("code_challenge")  # from CLI
    STATE_STORE.add(state)
    url = build_github_url(state, code_challenge)

    return JsonResponse({
        "auth_url": url,
        "state": state
    })

# API callback for GitHub OAuth (for mobile/third-party use)
@api_view(['POST'])
def github_callback(request):
    code = request.data.get("code")
    code_verifier = request.data.get("code_verifier")

    if not code or not code_verifier:
        return Response(
            {"status": "error", "message": "Invalid request"},
            status=400
        )

    # -------------------------
    # Exchange code with GitHub
    # -------------------------
    token_data = exchange_code_for_token(code, code_verifier)

    access_token = token_data.get("access_token")

    if not access_token:
        return Response(
            {"status": "error", "message": "GitHub auth failed"},
            status=400
        )

    # -------------------------
    # Get user info
    # -------------------------
    user_data = get_github_user(access_token)

    # -------------------------
    # Create/update user
    # -------------------------
    user = create_or_update_user(user_data)

    # -------------------------
    # Generate tokens
    # -------------------------
    access, refresh = generate_tokens(user)

    return Response({
        "status": "success",
        "access_token": access,
        "refresh_token": refresh,
        "username": user.username
    })

# Web callback for GitHub OAuth (for frontend use)
@api_view(['GET'])
def github_callback_web(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    code_verifier = request.GET.get("code_challenge")
    if state not in STATE_STORE:
        return JsonResponse(
            {"status": "error", "message": "Invalid state"},
            status=400
        )
    
    # Validate state
    if state != request.session.get("oauth_state"):
        return Response(
            {"status": "error", "message": "Invalid state"},
            status=400
        )

    # Exchange code
    token_res = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": os.getenv("GITHUB_CLIENT_ID"),
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
            "code": code,
            "code_verifier": code_verifier,

        },
        timeout=5
    ).json()

    access_token = token_res.get("access_token")

    if not access_token:
        return Response(
            {"status": "error", "message": "GitHub auth failed"},
            status=400
        )

    # Get user
    user_res = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=5
    ).json()

    user, _ = User.objects.update_or_create(
        github_id=user_res["id"],
        defaults={
            "username": user_res["login"],
            "avatar_url": user_res.get("avatar_url"),
            "email": user_res.get("email"),
            "last_login_at": timezone.now(),
        }
    )

    access, refresh = web_generate_tokens(user)

    return Response({
        "status": "success",
        "access_token": access,
        "refresh_token": refresh,
        "user": {
            "id": str(user.id),
            "username": user.username,
            "avatar_url": user.avatar_url,
            "role": user.role
        }
    })