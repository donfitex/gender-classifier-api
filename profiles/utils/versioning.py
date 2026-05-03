from rest_framework.response import Response

def check_version(request):
    version = request.headers.get("X-API-Version")

    if version != "1":
        return Response(
            {"status": "error", "message": "API version header required"},
            status=400
        )

    return None