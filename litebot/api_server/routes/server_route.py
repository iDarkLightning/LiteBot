from sanic.response import json as json_resp
from sanic.request import Request
from sanic.response import BaseHTTPResponse
from ...errors import ServerNotFound, ServerCommandNotFound
from ...minecraft.server import MinecraftServer
from sanic import exceptions
from sanic import Blueprint
from ..middlewares.jwt import validate_jwt_headers

blueprint = Blueprint("server", url_prefix="/server")

RECV_MESSAGE_ROUTE = "/recv_message"
RECV_COMMAND_ROUTE = "/recv_command"

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
        server = MinecraftServer.get_from_name(token_payload["server_name"])
    except KeyError:
        raise exceptions.NotFound("Invalid token payload!")
    except ServerNotFound:
        raise exceptions.NotFound(f"There is no server matching {token_payload['server_name']}")
    request.ctx.server = server


@blueprint.route(RECV_MESSAGE_ROUTE, methods=["POST"])
async def recv_message(request: Request) -> BaseHTTPResponse:
    """
    A POST method route at /recv_message.
    Sends the given message in the server's bridge channel

    Example Form Body
    ------------------
    {
        "message": "This is an example message"
    }

    :param request: The HTTPRequest object, provided by Sanic
    :type request: sanic.request.Request
    :return: A positive/negative response in application/json format
    :rtype: BaseHTTPResponse
    """
    data = request.json

    try:
        server: MinecraftServer = request.ctx.server
        await server.recieve_message(data["message"])
        return json_resp({
            "message": f"Message: {data['message']} has been sent successfully to {(await server.bridge_channel).name}"})
    except AttributeError:
        return json_resp({"message": "This server does not have a configured bridge channel!"}, status=500)

@blueprint.route(RECV_COMMAND_ROUTE, methods=["POST"])
async def recv_command(request: Request) -> BaseHTTPResponse:
    """
    A POST method rout at /recv_command.
    Executes the command provided.

    Example Form Body
    ------------------
    {
        "name": "command"
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
        server: MinecraftServer = request.ctx.server
        await server.recieve_command(data["name"], args)
        return json_resp({"message": f"Message: {data['name']} has been executed successfully!"})
    except ServerCommandNotFound:
        return json_resp({"message": "This is not a valid command!"}, status=401)
    except TypeError:
        return json_resp({"message": "Invalid arguments provided!"}, status=401)
    except Exception as e:
        return json_resp({"message": f"Command execution failed! Error: {e}"}, status=500)