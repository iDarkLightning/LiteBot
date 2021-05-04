import os
from typing import Coroutine, Any, Optional
from sanic import Sanic
from sanic.server import AsyncioServer
from .routes import ROUTES
from ..litebot import LiteBot
from sanic.log import logger, access_logger
from ..utils.logging import set_logger, set_access_logger
from sanic_cors import CORS

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

def get_server_coro(bot_instance: LiteBot) -> Coroutine[Any, Any, Optional[AsyncioServer]]:
    """
    Sets up a Sanic app and returns an AsyncioServer
    :return: An AsyncioServer with the Sanic App
    :rtype: AsyncioServer
    """
    app = Sanic(APP_NAME)
    CORS(app)

    # A stupid hackfix that I have to do to make the logging work appropriately
    # I don't like it, but I don't see a better way to achieve this
    # Personally I think this is cleaner then using the dictConfig
    set_logger(logger)
    set_access_logger(access_logger)

    app.config.FALLBACK_ERROR_FORMAT = "json"
    app.config.BOT_INSTANCE = bot_instance
    # This is set so that we can properly generate URLs to our server
    app.config.SERVER_NAME = os.environ.get("SERVER_NAME")
    add_routes(app)

    return app.create_server(host=SERVER_HOST, port=SERVER_PORT, return_asyncio_server=True, access_log=False)