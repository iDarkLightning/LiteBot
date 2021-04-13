from __future__ import annotations

import asyncio
from pathlib import Path
from .protocol.connection import UDPSocketConnection
from .protocol.query import ServerQuerier, QueryResponse
from .protocol.rcon import ServerRcon
from .server_commands.server_action import ServerCommand, ServerEvent
from .server_commands.server_context import ServerCommandContext, ServerEventContext
from ..errors import ServerConnectionFailed, ServerNotFound, ServerNotRunningLTA, ServerNotRunningCarpet
from ..utils import requests
from socket import timeout
from typing import Optional, List, Tuple
from jwt import encode as jwt_encode
from discord import TextChannel
from discord.errors import NotFound
import datetime
from datetime import datetime, timedelta
import os
from discord import Message

from ..utils.data_manip import parse_emoji
from ..utils.enums import BackupTypes

SERVER_DIR_NAME = "servers"
BACKUP_DIR_NAME = "backups"
DEFAULT_WORLD_DIR_NAME = "world"
CHAT_MESSAGE_ROUTE = "/chat_message"
SYSTEM_MESSAGE_ROUTE = "/system_message"
TPS_COMMAND = "script run reduce(last_tick_times(),_a+_,0)/100;"

class MinecraftServer:
    """
    Modules communication to and from a minecraft server
    """
    instances = []

    def __init__(self, name: str, bot, **info: dict) -> None:
        self.name = name
        self.bot_instance = bot
        self._addr = info["numerical_server_ip"]
        self._port = info["server_port"]
        self._rcon = ServerRcon(self._addr, info["rcon_password"], info["rcon_port"])
        self.operator = info["operator"]
        self._lta_addr = info["litetech_additions"]["address"]
        self.bridge_channel_id = info["litetech_additions"]["bridge_channel_id"]
        self._add_instance(self)

    @property
    def server_dir(self) -> Optional[str]:
        """
        :return: The server's directory if it exists, else returns None
        :rtype: Optional[str]
        """
        dir_ = os.path.join(os.getcwd(), SERVER_DIR_NAME, self.name)
        return dir_ if os.path.exists(dir_) else None

    @property
    def world_dir(self) -> Optional[str]:
        if not self.server_dir:
            return

        world_dir = os.path.join(self.server_dir, DEFAULT_WORLD_DIR_NAME)
        if os.path.exists(world_dir):
            return world_dir
        else:
            level_name = None
            with open(os.path.join(self.server_dir, "server.properties")) as f:
                props = {k: v.removesuffix("\n") for k,v in [line.split("=", 2) for line in f.readlines() if "=" in line]}
                level_name = props["level-name"]
            return os.path.join(self.server_dir, level_name)

    @property
    def backup_dir(self) -> Optional[str]:
        if not self.world_dir:
            return

        Path(os.path.join(self.server_dir, BACKUP_DIR_NAME)).mkdir(exist_ok=True)
        Path(os.path.join(self.server_dir, BACKUP_DIR_NAME, BackupTypes.MANUAL.value)).mkdir(exist_ok=True)
        Path(os.path.join(self.server_dir, BACKUP_DIR_NAME, BackupTypes.WEEKLY.value)).mkdir(exist_ok=True)

        return os.path.join(self.server_dir, BACKUP_DIR_NAME)

    @property
    def running_lta(self):
        return self._lta_addr and self.bridge_channel_id

    @property
    def bridge_channel(self) -> Optional[TextChannel]:
        """
        :return: The TextChannel object for the server's bridge channel
        :rtype: TextChannel
        """
        try:
            channel = self.bot_instance.get_channel(self.bridge_channel_id)
            return channel
        except NotFound:
            return None

    @classmethod
    def _add_instance(cls, instance: MinecraftServer) -> None:
        """
        Appends an instance of the class to a list of instances
        :param instance: The instance to append
        :type instance: MinecraftServer
        """
        cls.instances.append(instance)

    @classmethod
    def get_from_name(cls, name: str) -> MinecraftServer:
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

    @classmethod
    def get_from_channel(cls, id_: int) -> MinecraftServer:
        """
        Gets a server from it's bridge channel id
        :param id_: The ID of the pridge channel
        :type id_: int
        :return: An instance of a Minecraft Server
        :rtype: MinecraftServer
        :raises: ServerNotFound
        """
        server = list(filter(lambda s: s.bridge_channel_id == id_, cls.instances))
        if len(server) > 0:
            return server[0]
        else:
            raise ServerNotFound

    @classmethod
    def get_all_instances(cls) -> List[MinecraftServer]:
        """
        Gets all server instances
        :return: A list with all current instances of servers
        :rtype: List[MinecraftServer]
        """
        return cls.instances

    @classmethod
    def get_first_instance(cls) -> MinecraftServer:
        """
        Get's the first server instantiated.
        :return: The first server instantiated
        :rtype: MinecraftServer
        """
        return next(iter(cls.instances))

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

    def tps(self) -> Tuple[float, float]:
        """
        Get's the server's TPS and MSPT.
        The result is the average of the past 100 ticks
        :return: The server's TPS and MSPT
        :rtype: Tuple[float, float]
        """
        res = self.send_command(TPS_COMMAND)
        try:
            float(res.split()[1])
        except ValueError:
            raise ServerNotRunningCarpet

        mspt = round(float(res.split()[1]), 1)
        tps = 20.0 if mspt <= 50.0 else 1000 / mspt
        return mspt, round(float(tps), 1)

    async def stop(self) -> bool:
        """
        Stops the server
        :return: The online status of the server
        :rtype: bool
        """
        server_online = True

        while server_online:
            try:
                self.send_command("stop")
                server_online= self.status().online
                await asyncio.sleep(2)
            except ServerConnectionFailed:
                server_online = False

        return server_online

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

    async def dispatch_message(self, message: str) -> None:
        """
        Sends a given message to the server's bridge channel
        :param message: The message to send
        :type message: str
        :raises: AttributeError
        """

        message = await parse_emoji(self.bot_instance, message)
        await (await self.bridge_channel).send(message)

    async def dispatch_command(self, author: str, command: str, sub: str, args: Tuple[str]) -> None:
        """
        Executes a command sent from the server
        :param author: The UUID of the player who executed the command
        :type author: str
        :param command: The name of the command
        :type command: str
        :param sub: The sub command
        :type sub: str
        :param args: The arguments for the command
        :type args: Tuple[str]
        """
        command = ServerCommand.get_from_name(command)
        ctx = ServerCommandContext(self, self.bot_instance, author)

        if sub:
            await command.invoke_sub(ctx, sub, args)
        else:
            await command.invoke(ctx, args)

    async def dispatch_event(self, event: str, author: Optional[str], args: Tuple[str]) -> None:
        events = ServerEvent.get_from_name(event)
        ctx = ServerEventContext(self, self.bot_instance, author)

        for event in events:
            await event.invoke(ctx, args)

    async def _send_server_message(self, route: str, message: dict, payload: Optional[dict] = None) -> dict:
        """
        Signs a JWT token and sends a message to the server
        :param route: The route to send the message to
        :type route: str
        :param payload: The payload for the JWT Token
        :type payload: dict
        :param message: The message to send
        :type message: dict
        :return: The server's response
        :rtype: dict
        :raises: ServerConnectionFailed
        """

        if payload is None:
            payload = {}
        payload["exp"] = datetime.utcnow() + timedelta(seconds=30)

        jwt_token = jwt_encode(payload, self.bot_instance.config["api_secret"])

        try:
            return requests.post((self._lta_addr + route),
                          data=message, headers={"Authorization": "Bearer " + jwt_token})
        except Exception as e:
            raise ServerConnectionFailed(e)

    async def send_discord_message(self, message: Message) -> dict:
        """
        Sends a discord chat message to the server, only works if server is running LTA

        :param message: The message to send
        :type message: discord.Message
        :return: The server's response
        :rtype: dict
        :raises: ServerNotRunningLTA
        :raises: ServerConnectionFailed
        """
        if not self._lta_addr:
            raise ServerNotRunningLTA

        data = {
            "userName": message.author.display_name,
            "userRoleColor": message.author.color.value
        }

        if len(message.content) > 0:
            data["messageContent"] = message.clean_content

        if message.attachments:
            data["attachments"] = {attachment.filename: attachment.url for attachment in message.attachments}

        return await self._send_server_message(CHAT_MESSAGE_ROUTE, data)

    async def send_message(self, text, op_only=False, player=None) -> dict:
        """
        Sends a system message to the server, only works if server is running LTA

        Example Message
        ----------------
        {
            "message": "This is an example message",
            "color": 16777215
        }

        :param text: The text to send to the server
        :type text: litebot.minecraft.text.Text
        :param player: The player to send the message to
        :param op_only: Whether the message is only for OP players
        :return: The server's response
        :rtype: dict
        :raises: ServerNotRunningLTA
        :raises: ServerConnectionFailed
        """
        if not self._lta_addr:
            raise ServerNotRunningLTA

        payload = {}
        if op_only:
            payload["opOnly"] = op_only
        if player:
            payload["player"] = player

        data = text.build()

        return await self._send_server_message(SYSTEM_MESSAGE_ROUTE, data, payload)
