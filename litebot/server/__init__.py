from __future__ import annotations

import os

from sanic import Sanic
from .routes import ROUTES

APP_NAME = "LiteBot-API"
SERVER_HOST = "0.0.0.0"
SERVER_PORT = os.environ.get("SERVER_PORT")
SERVER_DOMAIN = os.environ.get("SERVER_DOMAIN")

def add_routes(app: Sanic) -> None:
    """
    Add all the routes to the app instance
    :param app: The app instance to add the routes to
    :type app: Sanic
    """
    app.blueprint(ROUTES)

