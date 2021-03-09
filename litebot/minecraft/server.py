from ..litebot import LiteBot
from ..utils.config import ConfigMap
from .protocol.connection import UDPSocketConnection
from .protocol.query import ServerQuerier, QueryResponse
from .protocol.rcon import ServerRcon
from ..errors import ServerConnectionFailed, ServerNotFound, ServerNotRunningLTA
from ..utils import requests
from socket import timeout
from typing import Optional
from async_property import async_property
from jwt import encode as jwt_encode
from discord import TextChannel
from discord.errors import NotFound
import datetime
from datetime import datetime
import os

SERVER_DIR_NAME = "servers"
CHAT_MESSAGE_ROUTE = "/game_message"
SYSTEM_MESSAGE_ROUTE = "/system_message"

class MinecraftServer:
    """
    Modules communication to and from a minecraft server
    """
    instances = []

    def __init__(self, name: str, bot: LiteBot, **info: ConfigMap) -> None:
        info = ConfigMap(value=info)
        self.name = name
        self._bot_instance = bot
        self._addr = info.numerical_server_ip
        self._port = info.server_port
        self._rcon = ServerRcon(self._addr, info.rcon_password, info.rcon_port)
        self.operator = info.operator
        self._lta_addr = info.litetech_additions.address
        self._bridge_channel_id = info.litetech_additions.bridge_channel_id
        self._add_instance(self)

    @property
    def server_dir(self) -> Optional[str]:
        """
        :return: The server's directory if it exists, else returns None
        :rtype: Optional[str]
        """
        dir_ = os.path.join(os.getcwd(), SERVER_DIR_NAME, self.name)
        return dir_ if os.path.exists(dir_) else None

    @async_property
    async def bridge_channel(self) -> Optional[TextChannel]:
        """
        :return: The TextChannel object for the server's bridge channel
        :rtype: TextChannel
        """
        try:
            channel = await self._bot_instance.fetch_channel(self._bridge_channel_id)
            return channel
        except NotFound:
            return None

    @classmethod
    def _add_instance(cls, instance) -> None:
        """
        Appends an instance of the class to a list of instances
        :param instance: The instance to append
        :type instance: MinecraftServer
        """
        cls.instances.append(instance)

    @classmethod
    def get_from_name(cls, name: str):
        """
        Gets a server from its name
        :param name: The name of the server to retrieve
        :type name: str
        :return: An instance of a Minecraft Server
        :rtype: MinecraftServer
        :raises: ServerNotFound
        """
        server = list(filter(lambda s: s.name == name, cls.instances))
        if len(server) > 0:
            return server[0]
        else:
            raise ServerNotFound

    def status(self) -> QueryResponse:
        """
        Gets the status of the server including online players
        :return: A QueryResponse with the server status
        :rtype: QueryResponse
        :raises: ServerConnectionFailed
        """
        try:
            connection = UDPSocketConnection((self._addr, self._port))
            querier = ServerQuerier(connection)
            querier.handshake()
            return querier.read_query()
        except timeout:
            return QueryResponse(status=False)
        except Exception:
            raise ServerConnectionFailed

    def send_command(self, command: str) -> Optional[str]:
        """
        Executes a command on the server
        :param command: The command to send to the server
        :type command: str
        :return: The server's response to the command
        :rtype: str
        :raises: ServerConnectionFailed
        """
        try:
            self._rcon.connect()
        except Exception:
            raise ServerConnectionFailed

        resp = self._rcon.command(command)

        if resp:
            return resp

    async def recieve_message(self, message: str) -> None:
        """
        Sends a given message to the server's bridge channel
        :param message: The message to send
        :type message: str
        :raises: TypeError
        """
        await self.bridge_channel.send(message)

    async def _send_server_message(self, route: str, message: dict) -> dict:
        """
        Signs a JWT token and sends a message to the server
        :param message: The message to send
        :type message: dict
        :return: The server's response
        :rtype: dict
        :raises: ServerConnectionFailed
        """

        jwt_token = jwt_encode(
            {"user": self._bot_instance.user.id, "exp": datetime.utcnow() + datetime.timedelta(seconds=30)},
            self._bot_instance.config.api_secret)

        try:
            return await requests.post(
            (self._lta_addr + route), data=message, headers={"Authorization": "Bearer " + jwt_token})
        except Exception as e:
            raise ServerConnectionFailed(e)

    async def send_chat_message(self, message: dict) -> dict:
        """
        Sends a discord chat message to the server, only works if server is running LTA

        Example Message
        ----------------
        {
            "userName": iDarkLightning,
            "userRoleColor": 16777215,
            "messageContent": "This is an example message",
            "attachments": {
                "filename.jpg": "file_url"
            }
        }

        :param message: The message to send to the server
        :type message: dict
        :return: The server's response
        :rtype: dict
        :raises: ServerNotRunningLTA
        :raises: ServerConnectionFailed
        """
        if not self._lta_addr:
            raise ServerNotRunningLTA

        return await self._send_server_message(CHAT_MESSAGE_ROUTE, message)

    async def send_system_message(self, message: dict) -> dict:
        """
        Sends a system message to the server, only works if server is running LTA

        Example Message
        ----------------
        {
            "message": "This is an example message",
            "color": 16777215
        }
        :param message: The message to send to the server
        :type message: dict
        :return: The server's response
        :rtype: dict
        :raises: ServerNotRunningLTA
        :raises: ServerConnectionFailed
        """
        if not self._lta_addr:
            raise ServerNotRunningLTA

        return await self._send_server_message(SYSTEM_MESSAGE_ROUTE, message)

