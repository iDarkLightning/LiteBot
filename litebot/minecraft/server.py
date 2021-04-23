from __future__ import annotations

import asyncio
import json
import os
import datetime

from typing import Optional, List, Tuple, TYPE_CHECKING
from jwt import encode as jwt_encode
from discord import TextChannel
from discord.errors import NotFound
from datetime import datetime, timedelta
from discord import Message
from pathlib import Path
from socket import timeout, inet_aton

from websockets import WebSocketCommonProtocol

from .protocol.connection import UDPSocketConnection
from .protocol.query import ServerQuerier, QueryResponse
from .protocol.rcon import ServerRcon
from .commands.action import ServerCommand, ServerEvent
from .commands.context import ServerCommandContext, ServerEventPayload
from ..errors import ServerConnectionFailed, ServerNotFound, ServerNotRunningCarpet
from ..utils import requests
from ..utils.data_manip import parse_emoji
from ..utils.enums import BackupTypes
from .text import Text

if TYPE_CHECKING:
    from litebot.litebot import LiteBot

SERVER_DIR_NAME = "servers"
BACKUP_DIR_NAME = "backups"
DEFAULT_WORLD_DIR_NAME = "world"
TPS_COMMAND = "script run reduce(last_tick_times(),_a+_,0)/100;"

class ServerContainer:
    def __init__(self):
        self._list = []

    def __iter__(self):
        for i in self._list:
            yield i

    def append(self, item):
        self._list.append(item)

    def get_from_name(self, name: str) -> MinecraftServer:
        """
        Gets a server from its name
        :param name: The name of the server to retrieve
        :type name: str
        :return: An instance of a Minecraft Server
        :rtype: MinecraftServer
        :raises: ServerNotFound
        """
        server = list(filter(lambda s: s.name == name, self._list))
        if len(server) > 0:
            return server[0]
        else:
            raise ServerNotFound

    def get_from_channel(self, id_: int) -> MinecraftServer:
        """
        Gets a server from it's bridge channel id
        :param id_: The ID of the pridge channel
        :type id_: int
        :return: An instance of a Minecraft Server
        :rtype: MinecraftServer
        :raises: ServerNotFound
        """
        server = list(filter(lambda s: s.bridge_channel_id == id_, self._list))
        if len(server) > 0:
            return server[0]
        else:
            raise ServerNotFound

    def get_all_instances(self) -> List[MinecraftServer]:
        """
        Gets all server instances
        :return: A list with all current instances of servers
        :rtype: List[MinecraftServer]
        """
        return self._list

    def get_first_instance(self) -> MinecraftServer:
        """
        Get's the first server instantiated.
        :return: The first server instantiated
        :rtype: MinecraftServer
        """
        return next(iter(self._list))

class MinecraftServer:
    """
    Modules communication to and from a minecraft server
    """
    def __init__(self, name: str, bot: LiteBot, **info: dict) -> None:
        self.name = name
        self.bot_instance = bot
        self.operator = info["operator"]
        self.bridge_channel_id = info["bridge_channel_id"]
        self._addr = info["numerical_server_ip"]
        self._port = info["server_port"]
        self._rcon = ServerRcon(self._addr, info["rcon_password"], info["rcon_port"])

        if self.bot_instance.using_lta:
            self._connection: Optional[WebSocketCommonProtocol] = None

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

    @property
    def connected(self):
        return bool(self._connection) and self._connection.open

    async def connect(self, socket: WebSocketCommonProtocol):
        self._connection = socket
        self.bot_instance.logger.info(f"WebSocket connection established to {self.name}")

        await self._connection.send(json.dumps({"commandData": ServerCommand.get_built()}))

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
            return QueryResponse(status=False)

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

    async def dispatch(self, action, data):
        meth = getattr(self, "dispatch_" + action, None)

        if meth:
            return await meth(data)

        return await self.send_message(Text.op_message("LiteBot: Sent invalid action!"), op_only=True)

    async def fetch(self, obj, data):
        meth = getattr(self, "fetch_" + obj, None)

        if meth:
            return await meth(data)

        return []

    async def dispatch_command(self, data):
        command = ServerCommand.get_from_name(data["name"])
        ctx = ServerCommandContext(self, self.bot_instance, data["player"])

        args = [command.arg_types[i](a).val for i, a in enumerate(data.get("args", []))]

        try:
            await command.invoke(ctx, args)
        except TypeError:
            pass

    async def dispatch_event(self, data):
        events = ServerEvent.get_from_name(data["name"])
        payload = ServerEventPayload(self, self.bot_instance, data["name"], args=data.get("args"))

        for event in events:
            await event.invoke(payload)

    async def fetch_suggester(self, data):
        command = ServerCommand.get_from_name(data["name"])
        ctx = ServerCommandContext(self, self.bot_instance, data["player"])

        suggestor = command.suggestors[data["arg"]]()

        return await suggestor.suggest(ctx, data["arg"], data["args"])

    async def recv_message(self, message: str) -> None:
        """
        Sends a given message to the server's bridge channel
        :param message: The message to send
        :type message: str
        :raises: AttributeError
        """
        message = await parse_emoji(self.bot_instance, message)
        await self.bridge_channel.send(message)

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

    async def send_message(self, text, op_only=False, player=None) -> None:
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
        message = text.build()
        payload = {"message": message}

        if op_only:
            payload["opOnly"] = op_only
        if player:
            payload["player"] = player

        await self._connection.send(json.dumps({"messageData": payload}))

