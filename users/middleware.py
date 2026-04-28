import jwt
from django.conf import settings
from django.http import JsonResponse
from .models import User

# Process incoming requests to check for valid JWT tokens and set request.user
class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.path.startswith("/api/"):
            auth = request.headers.get("Authorization")

            if not auth:
                return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)

            try:
                token = auth.split(" ")[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

                user = User.objects.get(id=payload["user_id"])

                if not user.is_active:
                    return JsonResponse({"status": "error", "message": "Forbidden"}, status=403)

                request.user = user

            except:
                return JsonResponse({"status": "error", "message": "Invalid token"}, status=401)

        return self.get_response(request)