import os

from flask import Flask

app = Flask(__name__)
# Required for flash messages (used by the error/success banners). In production
# set SECRET_KEY to a strong random value via the hosting environment.
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-only-insecure-secret-change-me"
)

from app import views  # noqa: E402,F401
