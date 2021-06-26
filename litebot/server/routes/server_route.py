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
    """
    A websocket route at / that is used to establish a connection with the server.
    Excpects messages to be sent in a JSON format
    Once a connection is established, it is used to communicate with the server.
    Each time the server sends data, it must include a `auth` JWT token.
    The token payload must contain the name of the server that the data is coming from, as well as the action that is being performed.

    Example Payload
    ----------------
    {
        "server_name": "smp",
        "action": "event"
    }

    :param request: The HTTPRequest object, provided by Sanic
    :type request: sanic.request.Request
    :param socket: The Websocket object, provided by Sanic
    :type socket: WebSocketCommonProtocol
    """
    async for message in socket:
        try:
            data: dict = json.loads(message)
            payload = validate_jwt(data["auth"], request.app.config.BOT_INSTANCE.config["api_secret"])
            server = request.app.config.BOT_INSTANCE.servers[payload["server_name"]]

            if not server.connected:
                await server.connect(socket)
            else:
                res = await server.dispatch(payload["action"], data)
                if res is not None:
                    await socket.send(json.dumps({"id": data["auth"], "res": res}))
        except AuthFailure:
            await socket.close(reason="Invalid Authorization Token!")
        except (KeyError, json.JSONDecodeError, ServerNotFound):
            await socket.send(json.dumps({"error": "Invalid Data!"}))

@blueprint.route(FETCH_ROUTE, methods=["GET"])
async def _fetch(request: Request, item: str):
    """
    A GET request route at /fetch/:item.
    Intended to be used by the server to fetch LiteBot data at runtime.
    For example, command suggestions.
    The request headers must contain an authorization token, with the server name.
    :param request: The HTTPRequest object, provided by Sanic
    :type request: sanic.request.Request
    :param item: The name item that is being requested
    :type item: str
    """
    payload = await validate_jwt_headers(request, request.app.config.BOT_INSTANCE.config["api_secret"])

    try:
        server = request.app.config.BOT_INSTANCE.servers[payload["server_name"]]
        return response.json(await server.fetch(item, json.loads(request.args.get("data"))))
    except (ServerNotFound, KeyError):
        raise exceptions.NotFound("Invalid token payload!")