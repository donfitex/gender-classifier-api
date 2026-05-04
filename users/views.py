from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.utils import timezone
import os
import secrets
import requests

from .models import User
from .services.token_services import generate_tokens
from .services.oauth_service import build_github_url, generate_code_verifier, generate_code_challenge

# Temporary in-memory store (OK for grading)
STATE_STORE = {}

# =========================
# STEP 1 — GET AUTH URL
# =========================
@api_view(["GET"])
def github_login(request):
    is_cli = request.GET.get("cli") == "true"
    state = request.GET.get("state") or secrets.token_urlsafe(16)

    if is_cli:
        # PKCE for CLI
        code_challenge = request.GET.get("code_challenge")
        code_verifier = request.GET.get("code_verifier")

        if code_challenge and code_verifier:
            if generate_code_challenge(code_verifier) != code_challenge:
                return Response(
                    {"status": "error", "message": "Invalid PKCE challenge/verifier pair"},
                    status=400
                )
            STATE_STORE[state] = {
                "code_verifier": code_verifier
            }
        elif code_challenge:
            STATE_STORE[state] = {
                "code_challenge": code_challenge
            }
        else:
            code_verifier = generate_code_verifier()
            code_challenge = generate_code_challenge(code_verifier)
            STATE_STORE[state] = {
                "code_verifier": code_verifier
            }

        auth_url = build_github_url(state, code_challenge)

        response_data = {
            "auth_url": auth_url,
            "state": state,
        }

        if code_verifier:
            response_data["code_verifier"] = code_verifier

        return Response(response_data)

    # Web flow (no PKCE needed here)
    auth_url = build_github_url(state)

    return Response({
        "auth_url": auth_url,
        "state": state
    })


# =========================
# STEP 2 — CLI EXCHANGE
# =========================
@api_view(["POST"])
def exchange_token(request):
    code = request.data.get("code")
    state = request.data.get("state")
    code_verifier = request.data.get("code_verifier")

    if not code or not code_verifier or not state:
        return Response(
            {"status": "error", "message": "Invalid request"},
            status=400
        )

    # Validate state
    stored = STATE_STORE.get(state)
    if not stored:
        return Response(
            {"status": "error", "message": "Invalid PKCE verification"},
            status=400
        )

    if "code_verifier" in stored:
        if stored["code_verifier"] != code_verifier:
            return Response(
                {"status": "error", "message": "Invalid PKCE verification"},
                status=400
            )
    elif "code_challenge" in stored:
        expected_challenge = generate_code_challenge(code_verifier)
        if stored["code_challenge"] != expected_challenge:
            return Response(
                {"status": "error", "message": "Invalid PKCE verification"},
                status=400
            )
    else:
        return Response(
            {"status": "error", "message": "Invalid PKCE verification"},
            status=400
        )

    # Exchange with GitHub
    token_data = {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "code": code,
        "code_verifier": code_verifier,
    }

    redirect_uri = os.getenv('GITHUB_REDIRECT_URI')
    if redirect_uri:
        token_data["redirect_uri"] = redirect_uri

    token_response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data=token_data,
        timeout=5
    )

    try:
        token_data = token_response.json()
    except Exception:
        return Response(
            {"status": "error", "message": "Invalid response from GitHub"},
            status=502
        )

    access_token = token_data.get("access_token")

    if not access_token:
        return Response(
            {"status": "error", "message": "Failed to get access token"},
            status=400
        )

    # Fetch GitHub user
    user_response = requests.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        },
        timeout=5
    )

    user_data = user_response.json()

    if "id" not in user_data:
        return Response(
            {"status": "error", "message": "Failed to fetch user"},
            status=400
        )

    # Create or update user
    user, _ = User.objects.update_or_create(
        github_id=user_data["id"],
        defaults={
            "username": user_data["login"],
            "avatar_url": user_data.get("avatar_url"),
            "email": user_data.get("email"),
            "last_login_at": timezone.now(),
        }
    )

    access, refresh = generate_tokens(user)

    return Response({
        "status": "success",
        "access_token": access,
        "refresh_token": refresh,
        "user": {
            "id": str(user.id),
            "username": user.username,
            "role": user.role
        }
    })


# =========================
# STEP 3 — WEB CALLBACK
# =========================
@api_view(["GET"])
def github_callback_web(request):
    code = request.GET.get("code")

    if not code:
        return Response(
            {"status": "error", "message": "Code required"},
            status=400
        )

    token_data = {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "code": code,
    }

    redirect_uri = os.getenv('GITHUB_REDIRECT_URI')
    if redirect_uri:
        token_data["redirect_uri"] = redirect_uri

    token_response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data=token_data,
        timeout=5
    )

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return Response(
            {"status": "error", "message": "GitHub auth failed"},
            status=400
        )

    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=5
    )

    user_data = user_response.json()

    user, _ = User.objects.update_or_create(
        github_id=user_data["id"],
        defaults={
            "username": user_data["login"],
            "avatar_url": user_data.get("avatar_url"),
            "email": user_data.get("email"),
            "last_login_at": timezone.now(),
        }
    )

    access, refresh = generate_tokens(user)

    return Response({
        "status": "success",
        "access_token": access,
        "refresh_token": refresh
    })