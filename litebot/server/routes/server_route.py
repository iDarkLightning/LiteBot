import json

from sanic.request import Request

from sanic import Blueprint
from ..middlewares.jwt import validate_jwt

from ...errors import AuthFailure, ServerNotFound

blueprint = Blueprint("server", url_prefix="/server")

FETCH_ROUTE = "/fetch/<item:string>"

@blueprint.websocket("/")
async def _websocket(request: Request, socket):
    """A websocket route at / that is used to establish a connection with the server.

    Excpects messages to be sent in a JSON format
    Once a connection is established, it is used to communicate with the server.
    Each time the server sends data, it must include a `auth` JWT token.
    The token payload must contain the name of the server that the data is coming from, as well as the action that is being performed.

    Example:
        {
            "server_name": "smp",
            "action": "event"
        }

    """
    async for message in socket:
        try:
            data: dict = json.loads(message)
            payload = validate_jwt(data["auth"], request.app.config.BOT_INSTANCE.config["api_secret"])
            server = request.app.config.BOT_INSTANCE.servers[payload["server_name"]]

            if not server.server_connected:
                await server.connect_server(socket)
            else:
                res = await server.dispatch(payload["action"], data)
                if res is not None:
                    await socket.send(json.dumps({"id": data["auth"], "res": res}))
        except AuthFailure:
            await socket.close(reason="Invalid Authorization Token!")
        except (KeyError, json.JSONDecodeError, ServerNotFound):
            await socket.send(json.dumps({"error": "Invalid Data!"}))

