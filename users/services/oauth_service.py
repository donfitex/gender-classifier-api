import os
import base64
import hashlib
import secrets
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

def generate_code_verifier():
    return secrets.token_urlsafe(64)


def generate_code_challenge(verifier):
    return base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).decode().rstrip("=")


def build_github_url(state, code_challenge=None):
    params = {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "scope": "user",
        "state": state,
    }

    redirect_uri = os.getenv('GITHUB_REDIRECT_URI')
    if redirect_uri:
        params["redirect_uri"] = redirect_uri

    if code_challenge:
        params["code_challenge"] = code_challenge
        params["code_challenge_method"] = "S256"

    return "https://github.com/login/oauth/authorize?" + urlencode(params, safe="-_~")
