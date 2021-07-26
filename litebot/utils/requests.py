
from aiohttp import ClientSession, ContentTypeError, ClientResponse
from typing import Optional, Union

async def fetch(url: str, headers: Optional[dict] = None) -> Union[ClientResponse, dict]:
    """Makes an async get request and returns a dict with response application/json format response expected

    Args:
        url: The URL to make the request to
        headers: Any headers to include with the request

    Returns:
        The server's response in JSON format if possible, or just the response
    """
    async with ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            try:
                return await response.json()
            except ContentTypeError:
                return response

async def post(url: str, data: dict, headers: Optional[dict] = None) -> Union[ClientResponse, dict]:
    """Makes an async post request and returns a dict with response application/json format response expected

    Args:
        url: The URL to make the request to
        data: The data for the POST request body
        headers: Any headers to include with the request

    Returns:
        The server's response in JSON format
    """
    async with ClientSession() as session:
        async with session.post(url=url, data=str(data), headers=headers) as response:
            try:
                return await response.json()
            except ContentTypeError:
                return response

