from __future__ import annotations

from sanic import Sanic
from .routes import ROUTES

APP_NAME = "LiteBot-API"
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080

def add_routes(app: Sanic) -> None:
    """
    Add all the routes to the app instance
    :param app: The app instance to add the routes to
    :type app: Sanic
    """
    app.blueprint(ROUTES)

