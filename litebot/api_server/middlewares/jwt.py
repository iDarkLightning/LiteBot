from sanic.request import Request
from sanic import exceptions
import re, jwt
from typing import NoReturn, Union, Optional
from ...utils.logging import get_logger

logger = get_logger("bot")

async def validate_jwt(request: Request, secret: str, auth_scheme: Optional[str] ="Bearer") -> Union[NoReturn, dict]:
    """
    This validates a JWT in a HTTP Request and returns the decoded token
    :param request: The HTTP Reuqest that contains the token
    :type request: sanic.request.Request
    :param secret: The secret to decode the token with
    :type secret: str
    :param auth_scheme: The expected auth_scheme used for the token, "Bearer" by default
    :type auth_scheme: Optional[str]
    :return: The decoded JWT
    :rtype: Union[NoReturn, dict]
    """
    if "Authorization" not in request.headers:
        raise exceptions.Unauthorized("Missing Authorization Header!")

    try:
        scheme, token = request.headers.get("Authorization").strip().split(" ")
    except ValueError:
        raise exceptions.Forbidden("Invalid Authorization Header!")

    if not re.match(auth_scheme, scheme):
        raise exceptions.Forbidden("Invalid token scheme")

    if token:
        try:
            decoded = jwt.decode(token, secret, algorithms="HS256")
        except jwt.InvalidTokenError as jet:
            logger.exception(jet, exc_info=jet)
            raise exceptions.Unauthorized(message=f"Invalid Authorization token, {jet}")

        if decoded:
            return decoded