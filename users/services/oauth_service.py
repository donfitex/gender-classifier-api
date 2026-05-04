import os
import base64
import hashlib
import secrets
from dotenv import load_dotenv

load_dotenv()

def generate_code_verifier():
    return secrets.token_urlsafe(64)


def generate_code_challenge(verifier):
    return base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).decode().rstrip("=")


def build_github_url(state, code_challenge):
    client_id = os.getenv("GITHUB_CLIENT_ID")
    redirect_uri = os.getenv('GITHUB_REDIRECT_URI')
    
    return (
        "https://github.com/login/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=user"
        f"&state={state}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
    )