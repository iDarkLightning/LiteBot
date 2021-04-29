import os

from sanic import Blueprint, response, exceptions
from sanic.request import Request
from sanic.response import BaseHTTPResponse

from litebot.server.middlewares.jwt import validate_jwt_query
from litebot.errors import ServerNotFound
from litebot.minecraft.server import MinecraftServer

blueprint = Blueprint("backups", url_prefix="/backups")

DOWNLOAD_ROUTE = "/download/<backup_name:path>"

@blueprint.middleware("request")
async def _validate_jwt(request: Request) -> None:
    """
    Middleware to validate JWT in user's query params
    Tries to get the server provided in the token payload,
    and sets it in request.ctx.server.

    Example Token Payload
    ----------------------
    {
        "server_name": "smp"
    }

    :param request: The HTTPRequest object, provided by Sanic
    :type request: sanic.request.Request
    """

    token_payload = await validate_jwt_query(request, request.app.config.BOT_INSTANCE.config["api_secret"])
    try:
        server = request.app.config.BOT_INSTANCE.servers[token_payload["server_name"]]
    except KeyError:
        raise exceptions.NotFound("Invalid token payload!")
    except ServerNotFound:
        raise exceptions.NotFound(f"There is no server matching {token_payload['server_name']}")
    request.ctx.server = server


@blueprint.route(DOWNLOAD_ROUTE, methods=["GET"], name="download_backup")
async def download_backup(request: Request, backup_name: str) -> BaseHTTPResponse:
    """
    Sends the user the backup file for download.

    Example URL
    ------------
        http://localhost:8080/backups/download_backup/backup.zip

    :param request: The HTTPRequest object, provided by Sanic
    :type request: sanic.request.Request
    :param backup_name: The name of the backup, provided in the URL
    :type backup_name: str
    :return: The backup file
    :rtype: BaseHTTPResponse
    """

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