from sanic.request import Request
from sanic import exceptions
import re, jwt
from typing import NoReturn, Union, Optional
from ...utils.logging import get_logger

logger = get_logger("bot")
ALGORITHM = "HS256"

async def validate_jwt_headers(request: Request, secret: str, auth_scheme: Optional[str] = "Bearer") -> Union[NoReturn, dict]:
    """
    This validates a JWT in a HTTP Request Headers and returns the decoded token
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
            decoded = jwt.decode(token, secret, algorithms=ALGORITHM)
        except jwt.InvalidTokenError as jet:
            logger.exception(jet, exc_info=jet)
            raise exceptions.Unauthorized(message=f"Invalid Authorization token, {jet}")

        if decoded:
            return decoded

async def validate_jwt_query(request: Request, secret: str) -> Union[NoReturn, dict]:
    """
    This validates a JWT the request's query parameters
    :param request: The HTTP Reuqest that contains the token
    :type request: sanic.request.Request
    :param secret: The secret to decode the token with
    :type secret: str
    :return: The decoded JWT
    :rtype: Union[NoReturn, dict]
    """
    try:
        token = request.args["token"][0]
    except KeyError:
        raise exceptions.Forbidden("Missing token in request arguments!")

    try:
        decoded = jwt.decode(token, secret, algorithms=ALGORITHM)
    except jwt.InvalidTokenError as jet:
        logger.exception(jet, exc_info=jet)
        raise exceptions.Unauthorized(message=f"Invalid Authorization token, {jet}")

    if decoded:
        return decoded