import json as json

from sanic import Blueprint, exceptions
from sanic.request import Request
from sanic.response import BaseHTTPResponse, json as json_response

from litebot.server.middlewares.jwt import validate_jwt_headers
from plugins.standard.discord_utils.archives.archived_channel_model import ArchivedChannel

blueprint = Blueprint("archives", url_prefix="/archives")


@blueprint.middleware("request")
async def _validate_jwt(request: Request):
    payload = await validate_jwt_headers(request, request.app.config.BOT_INSTANCE.config["api_secret"])
    try:
        request.ctx.user = int(payload["userID"])
        request.ctx.channels = [o for o in ArchivedChannel.objects() if request.ctx.user in [u["id"] for u in o.users]]
    except (KeyError, ValueError):
        raise exceptions.NotFound("Invalid Token Payload!")


@blueprint.route("/", methods=["GET"])
async def _get_archives(request: Request) -> BaseHTTPResponse:
    """
    A GET request method at /archives to fetch all the current archives
    :param request: The HTTPRequest object, provided by Sanic
    :type request: sanic.request.Request
    :return: A json version of all the archived channels stored on the database, see `class:ArchivedChannel`
    :rtype: BaseHTTPResponse
    """
    return json_response([json.loads(o.to_json()) for o in request.ctx.channels])

@blueprint.route("/channels", methods=["GET"])
async def _get_archived_channels(request: Request) -> BaseHTTPResponse:
    return json_response([{
        "name": c.name,
        "id": str(c.channel_id),
        "category": c.category} for c in request.ctx.channels])

@blueprint.route("/channel/<id:int>", methods=["GET"])
async def _get_archived_channel(request: Request, id: int):
    try:
        channel = list(filter(lambda c: c.channel_id == id, request.ctx.channels))[0]
        return json_response({"res": json.loads(channel.to_json())})
    except IndexError:
        return json_response({"error": "no such channel found!"})

@blueprint.route("/channel/<id:int>/<message_index:int>", methods=["GET"])
async def _get_message(request, id: int, message_index: int):
    try:
        channel = list(filter(lambda c: c.channel_id == id, request.ctx.channels))[0]
        return json_response(json.loads(channel.to_json())["messages"][message_index])
    except IndexError:
        return json_response({"error": "no such channel found!"})

