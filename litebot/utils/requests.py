from aiohttp import ClientSession
from typing import Optional

async def fetch(url: str, headers: Optional[dict] = None) -> dict:
    """
    Makes an async get request and returns a dict with response
    application/json format response expected
    :param url: The URL to make the request to
    :type url: str
    :param headers: Any headers to make the request with
    :type headers: Optional[dict]
    :return: The server's response in JSON format
    :rtype: dict
    """
    async with ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()

async def post(url: str, data: dict, headers: Optional[dict] = None) -> dict:
    """
    Makes an async post request and returns a dict with response
    application/json format response expected
    :param headers: Any additional headers to include
    :type headers: Optional[dict]
    :param url: The URL to make the request to
    :type url: str
    :param data: The data to send to the server
    :type data: dict
    :return: The server's response in JSON format
    :rtype: dict
    """
    async with ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as response:
            return await response.json()