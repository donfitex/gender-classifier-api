def check_version(request):
    if request.headers.get("X-API-Version") != "1":
        return False
    return True