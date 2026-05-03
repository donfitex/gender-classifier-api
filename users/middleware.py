from time import time
from django.http import JsonResponse
from .services.token_services import TOKENS
from .models import User

RATE_LIMIT = {}


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time()

        # -----------------------------
        # RATE LIMITING
        # -----------------------------
        ip = request.META.get("REMOTE_ADDR")
        now = time()
        window = 60  # seconds

        if request.path.startswith("/auth/"):
            limit = 10
        else:
            limit = 60

        history = RATE_LIMIT.get(ip, [])

        # remove old requests
        history = [t for t in history if now - t < window]

        if len(history) >= limit:
            return JsonResponse(
                {"status": "error", "message": "Too many requests"},
                status=429
            )

        history.append(now)
        RATE_LIMIT[ip] = history

        # -----------------------------
        # AUTHENTICATION
        # -----------------------------
        if request.path.startswith("/api/"):

            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                return JsonResponse(
                    {"status": "error", "message": "Authentication required"},
                    status=401
                )

            token = auth_header.split(" ")[1]

            user_id = None
            for data in TOKENS.values():
                if data.get("access_token") == token:
                    user_id = data.get("user_id")
                    break  # IMPORTANT

            if not user_id:
                return JsonResponse(
                    {"status": "error", "message": "Invalid token"},
                    status=401
                )

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse(
                    {"status": "error", "message": "User not found"},
                    status=401
                )

            if not user.is_active:
                return JsonResponse(
                    {"status": "error", "message": "Forbidden"},
                    status=403
                )

            request.user = user

        # -----------------------------
        # PROCESS REQUEST
        # -----------------------------
        response = self.get_response(request)

        # -----------------------------
        # LOGGING
        # -----------------------------
        duration = time() - start
        print(f"{request.method} {request.path} {response.status_code} {duration:.3f}s")

        return response