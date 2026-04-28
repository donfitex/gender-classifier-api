import jwt
import datetime
from django.conf import settings

# JWT utility functions for generating access and refresh tokens
def generate_tokens(user):
    now = datetime.datetime.utcnow()

    access_payload = {
        "user_id": str(user.id),
        "exp": now + datetime.timedelta(minutes=3),
        "type": "access"
    }

    refresh_payload = {
        "user_id": str(user.id),
        "exp": now + datetime.timedelta(minutes=5),
        "type": "refresh"
    }

    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm="HS256")

    return access_token, refresh_token