from typing import Coroutine, Any, Optional
from sanic import Sanic
from sanic.server import AsyncioServer
from .routes import ROUTES
from ..litebot import LiteBot

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
    pass


def get_server_coro(bot_instance: LiteBot) -> Coroutine[Any, Any, Optional[AsyncioServer]]:
    """
    Sets up a Sanic app and returns an AsyncioServer
    :return: An AsyncioServer with the Sanic App
    :rtype: AsyncioServer
    """
    # TODO: Figure out better logging for Sanic
    app = Sanic(APP_NAME)
    app.config.FALLBACK_ERROR_FORMAT = "json"
    app.config.BOT_INSTANCE = bot_instance
    add_routes(app)

    return app.create_server(host=SERVER_HOST, port=SERVER_PORT, return_asyncio_server=True)