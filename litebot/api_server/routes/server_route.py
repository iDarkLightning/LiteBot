from sanic.response import json as json_resp
from sanic.request import Request
from sanic.response import BaseHTTPResponse
from litebot.errors import ServerNotFound, ServerActionNotFound
from ...minecraft.server import MinecraftServer
from sanic import exceptions
from sanic import Blueprint
from ..middlewares.jwt import validate_jwt_headers

blueprint = Blueprint("server", url_prefix="/server")

RECV_MESSAGE_ROUTE = "/recv_message"
RECV_COMMAND_ROUTE = "/recv_command"
RECV_EVENT_ROUTE = "/recv_event"

@blueprint.middleware("request")
async def _validate_jwt(request: Request) -> None:
    """
    Middleware to validate JWT in user's request
    Tries to get the server provided in the token payload,
    and sets it in request.ctx.server.

    Example Token Payload
    ----------------------
    {
        "server_name": "smp"
    }

    :param request:
    :type request:
    """
    token_payload = await validate_jwt_headers(request, request.app.config.BOT_INSTANCE.config["api_secret"])
    try:
        request.ctx.server = MinecraftServer.get_from_name(token_payload["server_name"])
        if "player" in token_payload:
            request.ctx.player = token_payload["player"]
    except KeyError:
        raise exceptions.NotFound("Invalid token payload!")
    except ServerNotFound:
        raise exceptions.NotFound(f"There is no server matching {token_payload['server_name']}")

@blueprint.route("/", methods=["GET"])
async def query_servers(request: Request) -> BaseHTTPResponse:
    """
    A GET method route at /.
    Returns the other servers registed.

    Does not include the server that the request originated from
    :param request: The HTTPRequest object, provided by Sanic
    :type request: sanic.request.Request
    :return: The servers response in application/json format
    :rtype: BaseHTTPResponse
    """
    return json_resp({"servers": [s.name for s in MinecraftServer.get_all_instances() if s.name != request.ctx.server.name]})

@blueprint.route(RECV_COMMAND_ROUTE, methods=["POST"])
async def _recv_command(request: Request) -> BaseHTTPResponse:
    """
    A POST method route at /recv_command.
    Executes the command provided.

    Example Form Body
    ------------------
    {
        "name": "command",
        "sub": "sub"
        "args" [
            "arg1",
            "arg2"
        ]
    }

    :param request: The HTTPRequest object, provided by Sanic
    :type request: sanic.request.Request
    :return: A positive/negative response in application/json format
    :rtype: BaseHTTPResponse
    """
    data: dict = request.json
    args = data.get("args") or []
    sub = data.get("sub")

    try:
        server: MinecraftServer = request.ctx.server
        await server.dispatch_command(request.ctx.player, data["name"], sub, args)
        return json_resp({"message": f"Message: {data['name']} has been executed successfully!"})
    except ServerActionNotFound:
        return json_resp({"message": "This is not a valid command!"}, status=401)
    except TypeError:
        return json_resp({"message": "Invalid arguments provided!"}, status=401)
    except Exception as e:
        return json_resp({"message": f"Command execution failed! Error: {e}"}, status=500)

@blueprint.route(RECV_EVENT_ROUTE, methods=["POST"])
async def _recv_event(request: Request) -> BaseHTTPResponse:
    """
    A POST method route at /recv_event.
    Executes the event provided.

    Events can have multiple accessors. All of the instances of the event will run.

    Example Form Body
    ------------------
    {
        "name": "event",
        "args" [
            "arg1",
            "arg2"
        ]
    }

    :param request: The HTTPRequest object, provided by Sanic
    :type request: sanic.request.Request
    :return: A positive/negative response in application/json format
    :rtype: BaseHTTPResponse
    """
    data: dict = request.json
    args = data.get("args") or []

    try:
        author = request.ctx.player
    except AttributeError:
        author = None

    try:
        server: MinecraftServer = request.ctx.server
        await server.dispatch_event(data["name"], author, args)
        return json_resp({"message": f"{data['name']} has been executed successfully!"})
    except (KeyError, ServerActionNotFound):
        return json_resp({"message": "This is not a valid event!"}, status=401)
    except TypeError:
        return json_resp({"message": "Invalid arguments provided!"}, status=401)
    except Exception as e:
        return json_resp({"message": f"Event execution failed! Error: {e}"}, status=500)