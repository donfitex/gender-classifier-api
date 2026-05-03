from django.http import JsonResponse
from .services.token_services import TOKENS
from .models import User

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only protect /api routes
        if request.path.startswith("/api/"):

            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                return JsonResponse(
                    {"status": "error", "message": "Authentication required"},
                    status=401
                )

            token = auth_header.split(" ")[1]

            # Find user via refresh store (simple approach)
            user_id = None
            for data in TOKENS.values():
                if data.get("access_token") == token:
                    user_id = data.get("user_id")

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

            # Attach user to request
            request.user = user

        return self.get_response(request)
