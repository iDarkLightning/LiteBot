import json

from sanic.request import Request

from sanic import Blueprint
from ..middlewares.jwt import validate_jwt
from websockets.protocol import WebSocketCommonProtocol

from ...errors import AuthFailure

blueprint = Blueprint("server", url_prefix="/server")

@blueprint.websocket("/")
async def _websocket(request: Request, socket: WebSocketCommonProtocol):
    async for message in socket:
        try:
            data = json.loads(message)
            payload = validate_jwt(data["auth"], request.app.config.BOT_INSTANCE.config["api_secret"])

            server = request.app.config.BOT_INSTANCE.servers.get_from_name(payload["server_name"])

            if not server.connected:
                await server.connect(socket)
            else:
                await server.dispatch(payload["action"], data)
        except AuthFailure:
            await socket.close(reason="Invalid Authorization Token!")
        except (KeyError, json.JSONDecodeError):
            await socket.send({"error": "Invalid Data!"})
