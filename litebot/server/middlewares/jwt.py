from sanic.request import Request
from sanic import exceptions
import re, jwt
from typing import NoReturn, Union, Optional

from litebot.errors import AuthFailure
from litebot.utils.logging import get_logger

logger = get_logger("bot")
ALGORITHMS = ["HS256", "HS512"]

def validate_jwt(token: str, secret: str) -> Optional[dict]:
    """Validate a JWT

    Args:
        token: The token to validate
        secret: The secret to validate the token with

    Returns:
        The decoded token payload

    Raises:
        AuthFailure
    """
    try:
        return jwt.decode(token, secret, algorithms=ALGORITHMS)
    except jwt.InvalidTokenError as e:
        raise AuthFailure(e)

async def validate_jwt_headers(request: Request, secret: str, auth_scheme: Optional[str] = "Bearer") -> Union[NoReturn, dict]:
    """Validate JWT in a HTTP Request Headers and returns the decoded token


    Args:
        request: The HTTP Reuqest that contains the token
        secret: The secret to validate the token with
        auth_scheme: The auth scheme used for the token, "Bearer" by default

    Returns:
        The decoded JWT

    Raises:
        exceptions.Forbidden
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
            decoded = jwt.decode(token.removesuffix("\n").removesuffix("\r"), secret, algorithms=ALGORITHMS)
        except jwt.InvalidTokenError as jet:
            logger.exception(jet, exc_info=jet)
            raise exceptions.Unauthorized(message=f"Invalid Authorization token, {jet}")

        if decoded:
            return decoded

async def validate_jwt_query(request: Request, secret: str) -> Union[NoReturn, dict]:
    """Validate JWT in a HTTP Request Query Parameters


    Args:
        request: The HTTP Reuqest that contains the token
        secret: The secret to validate the token with

    Returns:
        The decoded JWT

    Raises:
        exceptions.Forbidden
    """
    try:
        token = request.args["token"][0]
    except KeyError:
        raise exceptions.Forbidden("Missing token in request arguments!")

    try:
        decoded = jwt.decode(token, secret, algorithms=ALGORITHMS)
    except jwt.InvalidTokenError as jet:
        logger.exception(jet, exc_info=jet)
        raise exceptions.Unauthorized(message=f"Invalid Authorization token, {jet}")

    if decoded:
        return decoded