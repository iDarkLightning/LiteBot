from .litebot import LiteBot
from .api_server import get_server_coro
import asyncio
from .utils import requests

def main():
    bot_instance = LiteBot()

    bot_instance.init_modules()


    sanic_coro = get_server_coro(bot_instance)
    bot_instance.loop.create_task(sanic_coro)
    bot_instance.run(bot_instance.config["token"])

if __name__ == "__main__":
    main()