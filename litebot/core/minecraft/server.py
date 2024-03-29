from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from socket import timeout, gaierror, gethostbyname
from typing import Optional, Tuple, TYPE_CHECKING, Any

from discord import TextChannel
from discord.errors import NotFound
from websockets import WebSocketCommonProtocol

from litebot.errors import ServerConnectionFailed, ServerNotFound, ServerNotRunningCarpet
from .rpc import rpc
from .commands.context import ServerEventContext, RPCContext
from .commands.payload import Payload
from .player import Player
from .protocol import ServerQuerier, QueryResponse
from .protocol import ServerRcon
from .protocol import UDPSocketConnection
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

    @property
    def all(self) -> list[MinecraftServer]:
        return self._list

    def append(self, item: MinecraftServer):
        self._list.append(item)

    def get_server(self, ctx, name) -> MinecraftServer:
        if name:
            return self[name]
        else:
            return self[ctx.channel.id]

    def __getitem__(self, item) -> MinecraftServer:
        if isinstance(item, str):
            server = list(filter(lambda s: s.name == item, self._list))
        elif isinstance(item, int):
            server = list(filter(lambda s: s.bridge_channel_id == item, self._list))
        else:
            raise TypeError("Servers can only be retrieved through name or channel!")

        if len(server) > 0:
            return server[0]
        else:
            raise ServerNotFound

    def __iter__(self):
        for i in self._list:
            yield i


class MinecraftServer:
    """
    Modules communication to and from a minecraft server
    """

    def __init__(self, name: str, bot: LiteBot, **info) -> None:
        self.name = name
        self.bot_instance = bot
        self.operator = info["operator"]
        self.bridge_channel_id = info["bridge_channel_id"]
        self._addr = info["numerical_server_ip"]
        self._port = info["server_port"]
        self._rcon = ServerRcon(self.bot_instance.loop, self._addr, info["rcon_password"], info["rcon_port"])

        if self.bot_instance.using_lta:
            self._server_connection: Optional[WebSocketCommonProtocol] = None

        try:
            self._has_valid_addr = bool(gethostbyname(self._addr))
        except gaierror:
            self._has_valid_addr = False

    @property
    def server_dir(self) -> Optional[str]:
        """
        Returns:
            The server's directory if it exists, else None
        """
        dir_ = os.path.join(os.getcwd(), SERVER_DIR_NAME, self.name)
        return dir_ if os.path.exists(dir_) else None

    @property
    def world_dir(self) -> Optional[str]:
        """
        Returns:
            The server's world directory if it exists, else None
        """
        # TODO: change this to raise an error instead
        if not self.server_dir:
            return

        world_dir = os.path.join(self.server_dir, DEFAULT_WORLD_DIR_NAME)
        if os.path.exists(world_dir):
            return world_dir
        else:
            with open(os.path.join(self.server_dir, "server.properties")) as f:
                props = {k: v.removesuffix("\n") for k, v in
                         [line.split("=", 2) for line in f.readlines() if "=" in line]}
                level_name = props["level-name"]
            return os.path.join(self.server_dir, level_name)

    @property
    def backup_dir(self) -> Optional[str]:
        """
        Returns:
            The server's backups directory if it exists, else it will create it
        """
        # TODO: Change this to raise an error instead
        if not self.world_dir:
            return

        Path(os.path.join(self.server_dir, BACKUP_DIR_NAME)).mkdir(exist_ok=True)
        Path(os.path.join(self.server_dir, BACKUP_DIR_NAME, "manual")).mkdir(exist_ok=True)
        Path(os.path.join(self.server_dir, BACKUP_DIR_NAME, "weekly")).mkdir(exist_ok=True)

        return os.path.join(self.server_dir, BACKUP_DIR_NAME)

    @property
    def bridge_channel(self) -> Optional[TextChannel]:
        """
        Returns:
            The server's bridge channel
        """
        try:
            channel = self.bot_instance.get_channel(self.bridge_channel_id)
            return channel
        except NotFound:
            return None

    @property
    def server_connected(self):
        """
        Returns:
            Whether or not the server is connected via LiteBot-Mod
        """
        return bool(self._server_connection) and self._server_connection.open

    async def connect_server(self, socket: WebSocketCommonProtocol):
        """
        Connect the server's websocket connection to LiteBot-Mod

        Args:
            socket: The socket object being used to connect
        """
        self._server_connection = socket
        self.bot_instance.logger.info(f"WebSocket connection established to {self.name}")

        await self.send_command_tree()

    def status(self) -> QueryResponse:
        """Get the server status

        The server's status includes the MOTD and a list of online players

        Returns:
            A `QueryResponse` object containing the results from quering the server
        """
        if not self._has_valid_addr:
            return QueryResponse(status=False)

        try:
            connection = UDPSocketConnection((self._addr, self._port))
            querier = ServerQuerier(connection)
            querier.handshake()
            return querier.read_query()
        except timeout:
            return QueryResponse(status=False)
        except:
            return QueryResponse(status=False)

    async def tps(self) -> Tuple[float, float]:
        """Get the server's TPS and MSPT

        This is done via the use of Carpet-Mod. The result is
        the average of the past 100 ticks

        Returns:
            The server's TPS and MSPT
        """
        res = await self.send_command(TPS_COMMAND)
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
        """
        server_online = True

        while server_online:
            try:
                await self.send_command("stop")
                server_online = self.status().online
                await asyncio.sleep(2)
            except ServerConnectionFailed:
                server_online = False

        return server_online

    async def dispatch(self, action: str, data: dict) -> None:
        """Dispatches an action from the server.

        See methods starting with `dispatch_` to see actions that can be dispatched

        Args:
            action: The action that will be dispatched
            data: The data for the dispatching the action
        """
        meth = getattr(self, "_dispatch_" + action, None)
        if meth:
            return await meth(data)

        return await self.send_message(Text.op_message("LiteBot: Sent invalid action!"), op_only=True)

    async def _dispatch_command(self, data: dict):
        """Dispatches a command from the server

        Args:
            The data being used to dispatch the command
        """
        command = self.bot_instance.server_commands[data["name"]]
        ctx = command.create_context(self, self.bot_instance, data)

        try:
            for check in command.checks:
                if not check(ctx):
                    return await self.send_message(Text.error_message("You are not authorized to run this command!"))

            await ctx.invoke()
            await self._server_connection.send(json.dumps({
                "name": "server_command_after_invoke",
                "data": {"name": data["name"], "args": ctx.after_invoke_args}
            }))
        except TypeError as e:
            print(e)
            pass

    async def _dispatch_event(self, data: dict):
        """Dispatches an event from the server

        Args:
            The data being used to dispatch the event
        """
        events = self.bot_instance.server_events.get(data["name"], [])
        ctx = ServerEventContext(self, self.bot_instance, data.get("player", ""))
        payload = Payload.get_event_payload(data["name"])(ctx, data.get("args"))

        for event in events:
            args = (ctx.with_setting(event), payload) if hasattr(event, "__setting__") else (ctx, payload)
            asyncio.create_task(event(*args), name=f"{self.name}-event: {data['name']}")

    async def _dispatch_rpc(self, data: dict) -> Any:
        """Executes an RPC method from the server

        Args:
            data: The data being used to run the RPC method

        Returns:
            The result of the RPC method
        """

        if not (handler := self.bot_instance.rpc_handlers.get(
                data["name"],
                [getattr(self, m) for m in dir(self) if hasattr(getattr(self, m), "__rpc_handler__") and getattr(self, m).__name__ == data["name"]][0]
        )):
            return

        ctx = RPCContext(self, self.bot_instance, data)
        return await handler(ctx)

    @rpc(name="suggester")
    async def fetch_suggestions(self, ctx: RPCContext):
        command = self.bot_instance.server_commands[ctx.data["args"]["command_name"]]
        cmd_ctx = command.create_context(ctx.server, self.bot_instance, ctx.data)

        suggestor = command.suggestors[ctx.data["args"]["arg_name"]]()
        return await suggestor.suggest(cmd_ctx)

    async def send_command_tree(self):
        """Builds and sends the command tree to the server if the server is connected
        """
        if not self.server_connected:
            return

        data = []
        for s in self.bot_instance.server_commands.values():
            if s.parent:
                continue

            if all([await r(self.bot_instance, self) for r in s.requirements]):
                data.append(s.build())

        await self._server_connection.send(json.dumps({
            "name": "server_command_registers",
            "data": data
        }))

    async def send_command(self, command: str) -> Optional[str]:
        """Executes a command on the server

        Args:
            command: The command to send to the server

        Returns:
            The server's response from executing the command

        Raises:
            ServerConnectionFaield
        """
        if not self._has_valid_addr:
            raise ServerConnectionFailed

        try:
            await self._rcon.connect()
        except Exception:
            raise ServerConnectionFailed

        resp = await self._rcon.command(command)
        if resp:
            return resp

    def send_sync_command(self, command: str) -> Optional[str]:
        """Synchronously executes a command on the server

        This shouldn't be used in 99% of scenarios, the async version should
        be used instead.

        Args:
            command: The command to send to the server

        Returns:
            The server's response from executing the command

        Raises:
            ServerConnectionFaield
        """
        if not self._has_valid_addr:
            raise ServerConnectionFailed

        try:
            self._rcon.sync_connect()
        except:
            raise ServerConnectionFailed

        resp = self._rcon.sync_command(command)
        if resp:
            return resp

    async def send_message(self, text: Text, *, op_only: Optional[bool] = False,
                           player: Optional[Player] = None) -> None:
        """
        Sends a system message to the server, only works if server is running LTA

        Examples:
            {
                "message": "This is an example message",
                "color": 16777215
            }

        Args:
            text: The text to send to the server
            player: The player to send the message to
            op_only: Whether the message is only for OP players
        """
        if not self.server_connected:
            return

        message = text.build()
        payload = {"message": message}

        if op_only:
            payload["opOnly"] = op_only
        if player:
            payload["player"] = player.uuid

        await self._server_connection.send(json.dumps({"name": "message", "data": payload}))

