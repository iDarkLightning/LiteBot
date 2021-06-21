import asyncio
import socket
from typing import Optional, List

from litebot.core.minecraft import MinecraftServer, Player
from litebot.core.minecraft.text import Text, Colors

TWITCH_SERVER = "irc.chat.twitch.tv"
TWICH_PORT = 6667
BUF_SIZE = 2048
ENCODING = "utf-8"
PONG_MESSAGE = "PONG :tmi.twitch.tv\r\n".encode(ENCODING)

class Connection:
    """
    Models a connection to a twitch channel
    :param channel: The name of the channel
    :type channel: str
    :param sock: The socket connection to the channel
    :type sock: socket.socket
    :param color: The color to use for messages sent from this channel
    :type color: str
    """
    def __init__(self, channel: str, sock: socket.socket, color: str):
        self.channel = channel
        self.sock = sock
        self.color = color

class ConnectedPlayer:
    """
    Models a player who is connected to a channel
    :param server: The server that the player is on
    :type server: MinecraftServer
    :param player: The player
    :type player: Player
    """
    def __init__(self, server: MinecraftServer, player: Player):
        self.server = server
        self.player = player

class TwitchClient:
    def __init__(self, event_loop, config):
        self._loop = event_loop
        self._nick = config["nick"].lower()
        self._token = config["token"]
        self._client_id = config["client_id"]

    async def connect(self, channel: str) -> Optional[socket.socket]:
        """
        Connects to a twitch channel with a non-blocking socket
        :param channel: The channel to connect to
        :type channel: str
        :return: If a successful connection was made, then the connected socket object
        :rtype: Optional[socket.socket]
        """
        sock = socket.socket()
        sock.setblocking(False)

        if await self._handshake(sock, channel):
            return sock

    async def _handshake(self, sock: socket.socket, channel: str) -> bool:
        await self._loop.sock_connect(sock, (TWITCH_SERVER, TWICH_PORT))

        await self._loop.sock_sendall(sock, (f"PASS {self._token}\n".encode(ENCODING)))
        await self._loop.sock_sendall(sock, (f"NICK {self._nick}\n".encode(ENCODING)))
        await self._loop.sock_sendall(sock, (f"JOIN #{channel.lower()}\n".encode(ENCODING)))
        #receives and discards the data that is immediately sent back for every connection
        await self._loop.sock_recv(sock, BUF_SIZE)

        await asyncio.sleep(2)
        return bool((await self._loop.sock_recv(sock, BUF_SIZE)).decode(ENCODING))

    async def process_message(self, data: str, conn: Connection, connected_players: List[ConnectedPlayer]) -> None:
        """
        Processes new messages from a connected channel.
        If the message is a PING, then it sends back a PONG.
        Otherwise, it forwards the message to all the connected players
        :param data: The new data to process
        :type data: str
        :param conn: The connection to process the data for
        :type conn: Connection
        :param connected_players: All the players connected to the given connections
        :type connected_players: List[ConnectedPlayer]
        """
        msgs = data.split("\r\n")

        for msg in msgs:
            if "PING" in msg:
                await self._loop.sock_sendall(conn.sock, PONG_MESSAGE)

            try:
                src, _, channel, message = msg.split(" ", 3)
            except ValueError:
                continue

            text = Text()
            text.add_component(text=f"[{channel.replace(':', '').replace('#', '')}-stream] ", color=Colors.DARK_GRAY)
            text.add_component(text=src.split("!", 1)[0].replace(":", ""), color=conn.color)
            text.add_component(text=": " + message.replace(":", ""), color=Colors.WHITE)

            for player in connected_players:
                await player.server.send_message(text, player=player.player)
