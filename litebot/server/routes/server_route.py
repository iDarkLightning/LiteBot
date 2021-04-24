import json

from sanic.request import Request

from sanic import Blueprint, exceptions, response
from ..middlewares.jwt import validate_jwt, validate_jwt_headers
from websockets.protocol import WebSocketCommonProtocol

from ...errors import AuthFailure, ServerNotFound

blueprint = Blueprint("server", url_prefix="/server")

FETCH_ROUTE = "/fetch/<item:string>"

@blueprint.websocket("/")
async def _websocket(request: Request, socket: WebSocketCommonProtocol):
    async for message in socket:
        try:
            data = json.loads(message)
            payload = validate_jwt(data["auth"], request.app.config.BOT_INSTANCE.config["api_secret"])

            server = request.app.config.BOT_INSTANCE.servers[payload["server_name"]]

            if not server.connected:
                await server.connect(socket)
            else:
                await server.dispatch(payload["action"], data)
        except AuthFailure:
            await socket.close(reason="Invalid Authorization Token!")
        except (KeyError, json.JSONDecodeError, ServerNotFound):
            await socket.send({"error": "Invalid Data!"})

@blueprint.route(FETCH_ROUTE, methods=["GET"])
async def _fetch(request: Request, item: str):
    payload = await validate_jwt_headers(request, request.app.config.BOT_INSTANCE.config["api_secret"])

    try:
        server = request.app.config.BOT_INSTANCE.servers[payload["server_name"]]
        return response.json(await server.fetch(item, json.loads(request.args.get("data"))))
    except (ServerNotFound, KeyError):
        raise exceptions.NotFound("Invalid token payload!")