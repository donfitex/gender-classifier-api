from uuid6 import uuid7
from datetime import datetime, timedelta, timezone
import time

TOKENS = {}  # In-memory store for refresh tokens; in production, use a database or cache


def generate_tokens(user):
    access_token = str(uuid7())
    refresh_token = str(uuid7())

    # TOKENS[refresh_token] = {
    #     "user_id": str(user.id),
    #     "access_token": access_token,
    #     "access_expires": datetime.now(timezone.utc) + timedelta(minutes=3),
    #     "refresh_expires": datetime.now(timezone.utc) + timedelta(minutes=5),
    # }

    access_expires = time.time() + 180   # 3 minutes
    refresh_expires = time.time() + 300  # 5 minutes

    TOKENS[refresh_token] = {
        "user_id": str(user.id),
        "access_token": access_token,
        "access_expires": access_expires,
        "refresh_expires": refresh_expires
    }

    return access_token, refresh_token, access_expires, refresh_expires