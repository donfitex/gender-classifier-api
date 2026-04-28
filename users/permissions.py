from rest_framework.response import Response

# Decorator to check if the user is an admin
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role != "admin":
            return Response({"status": "error", "message": "Forbidden"}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper