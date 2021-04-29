import json as json
from sanic import Blueprint
from sanic.request import Request
from sanic.response import BaseHTTPResponse, json_response

from litebot.models.archived_channel_model import ArchivedChannel
from litebot.server.middlewares.jwt import validate_jwt_headers

blueprint = Blueprint("archives", url_prefix="/archives")

@blueprint.route("/", methods=["GET"])
async def _get_archives(request: Request) -> BaseHTTPResponse:
    """
    A GET request method at /archives to fetch all the current archives
    :param request: The HTTPRequest object, provided by Sanic
    :type request: sanic.request.Request
    :return: A json version of all the archived channels stored on the database, see `class:ArchivedChannel`
    :rtype: BaseHTTPResponse
    """
    await validate_jwt_headers(request, request.app.config.BOT_INSTANCE.config["api_secret"])

    return json_response([json.loads(o.to_json()) for o in ArchivedChannel.objects()])
