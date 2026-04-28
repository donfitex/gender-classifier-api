def check_version(request):
    return request.headers.get("X-API-Version") == "1"