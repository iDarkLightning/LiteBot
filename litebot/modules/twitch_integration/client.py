import asyncio
import socket

from litebot.utils import requests

TWITCH_SERVER = "irc.chat.twitch.tv"
TWICH_PORT = 6667
BUF_SIZE = 2048
ENCODING = "utf-8"
API_ROUTE = "https://api.twitch.tv/kraken"

class TwitchClient:
    def __init__(self, event_loop, config):
        self._loop = event_loop
        self._nick = config["nick"].lower()
        self._token = config["token"]
        self._client_id = config["client_id"]

    async def connect(self, channel: str) -> socket.socket:
        sock = socket.socket()
        sock.setblocking(False)

        if await self._handshake(sock, channel):
            return sock

    async def _handshake(self, sock: socket.socket, channel: str):
        await self._loop.sock_connect(sock, (TWITCH_SERVER, TWICH_PORT))

        await self._loop.sock_sendall(sock, (f"PASS {self._token}\n".encode(ENCODING)))
        await self._loop.sock_sendall(sock, (f"NICK {self._nick}\n".encode(ENCODING)))
        await self._loop.sock_sendall(sock, (f"JOIN #{channel.lower()}\n".encode(ENCODING)))
        await self._loop.sock_recv(sock, BUF_SIZE)

        await asyncio.sleep(2)
        res = (await self._loop.sock_recv(sock, BUF_SIZE)).decode(ENCODING)

        return bool(res)
