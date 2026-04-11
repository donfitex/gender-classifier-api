from .base import *

DEBUG = os.getenv("DEBUG") == "True"

ALLOWED_HOSTS = ["*"]  # Replace with your domain later

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True