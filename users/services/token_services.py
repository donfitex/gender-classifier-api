from uuid6 import uuid7
from datetime import datetime, timedelta

TOKENS = {}  # In-memory store for refresh tokens; in production, use a database or cache


def generate_tokens(user):
    access_token = str(uuid7())
    refresh_token = str(uuid7())

    TOKENS[refresh_token] = {
        "user_id": str(user.id),
        "access_token": access_token,
        "access_expires": datetime.now(datetime.timezone.utc) + timedelta(minutes=3),
        "refresh_expires": datetime.now(datetime.timezone.utc) + timedelta(minutes=5),
    }

    return access_token, refresh_token