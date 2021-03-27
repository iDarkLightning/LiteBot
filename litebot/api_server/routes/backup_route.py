import os

from sanic import Blueprint, response, exceptions
from sanic.request import Request
from sanic.response import BaseHTTPResponse

from litebot.api_server.middlewares.jwt import validate_jwt_query
from litebot.errors import ServerNotFound
from litebot.minecraft.server import MinecraftServer

blueprint = Blueprint("backups", url_prefix="/backups")

DOWNLOAD_ROUTE = "/download/<backup_name:path>"

@blueprint.middleware("request")
async def _validate_jwt(request: Request) -> None:
    token_payload = await validate_jwt_query(request, request.app.config.BOT_INSTANCE.config["api_secret"])
    try:
        server = MinecraftServer.get_from_name(token_payload["server_name"])
    except KeyError:
        raise exceptions.NotFound("Invalid token payload!")
    except ServerNotFound:
        raise exceptions.NotFound(f"There is no server matching {token_payload['server_name']}")
    request.ctx.server = server


@blueprint.route(DOWNLOAD_ROUTE, methods=["GET"], name="download_backup")
async def download_backup(request: Request, backup_name: str) -> BaseHTTPResponse:
    server: MinecraftServer = request.ctx.server

    backup_path = None

    for root, dirs, files in os.walk(server.backup_dir):
        for file in files:
            if file == backup_name:
                backup_path = os.path.join(root, file)

    if os.path.exists(backup_path):
        return await response.file(backup_path)
    else:
        raise exceptions.NotFound(f"There is no backup at path: {backup_path}")