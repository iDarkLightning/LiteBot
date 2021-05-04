import asyncio
import inspect
import traceback
from ast import literal_eval
from random import randint
from typing import List, Dict


from discord.ext import tasks
from litebot.core import Cog
import socket

from litebot.minecraft import commands
from litebot.litebot import LiteBot
from litebot.minecraft.commands.arguments import StringArgumentType, StrictSuggester
from litebot.minecraft.commands.context import ServerCommandContext
from litebot.minecraft.server import MinecraftServer
from litebot.minecraft.text import Text, Colors
from litebot.modules.twitch_integration.client import TwitchClient, ENCODING

TWITCH_SERVER = "irc.chat.twitch.tv"
TWICH_PORT = 6667
BUF_SIZE = 2048

class Connection:
    def __init__(self, channel: str, sock: socket.socket, color: str):
        self.channel = channel
        self.sock = sock
        self.color = color

class ConnectedPlayer:
    def __init__(self, server: MinecraftServer, player: str):
        self.server = server
        self.player = player

class ConnectedChannelSuggester(StrictSuggester):
    async def suggest(self, ctx: ServerCommandContext, arg: str, prior_args: dict) -> list:
        chat_cog = ctx.bot.get_cog("TwitchChat")
        to_suggest = []

        for channel in chat_cog.channels:
            connections = chat_cog.connections[channel]
            if ctx.player in [c.player for c in connections]:
                to_suggest.append(channel)

        return to_suggest

class TwitchChat(Cog):
    def __init__(self, bot: LiteBot):
        self._bot = bot
        self._config = self._bot.module_config["twitch_integration"]["config"]
        self._client = TwitchClient(self._bot.loop, self._config)
        self.channels = {}
        self.connections = {}

    @commands.command(name="stream")
    async def _stream(self, ctx: ServerCommandContext):
        """
        A namespace for declaring /stream subcommands
        """
        pass

    @_stream.sub(name="connect")
    async def _stream_connect(self, ctx: ServerCommandContext, channel: StringArgumentType):
        task = self.channels.get(channel)

        if not task:
            sock = await self._client.connect(channel)
            if not sock:
                return await ctx.send(
                    text=Text().add_component(text=f"Could not connect to {channel}-stream! Maybe try again?",
                                              color=Colors.RED))

            color = "#" + str(hex(randint(0, 16777215)))[2:]
            self.channels[channel] = self._bot.loop.create_task(self._receive_msgs(Connection(channel, sock, color)))

        players = self.connections.get(channel, [])
        players.append(ConnectedPlayer(ctx.server, ctx.player))
        self.connections[channel] = players

        await ctx.send(text=Text().add_component(text=f"Connected to {channel}-stream!", color=Colors.GREEN))

    @_stream.sub(name="view")
    async def _stream_view(self, ctx: ServerCommandContext):
        print(self.connections, self.channels)

    @_stream.sub(name="disconnect")
    async def _stream_disconnect(self, ctx: ServerCommandContext, channel: ConnectedChannelSuggester):
        self.connections[channel] = list(filter(lambda c: c.player != ctx.player, self.connections[channel]))

        if not len(self.connections[channel]):
            task = self.channels[channel]
            print(asyncio.get_running_loop())
            try:
                task.cancel()
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)

            del self.channels[channel]

        await ctx.send(text=Text().add_component(text=f"Disconnected from {channel}-stream!", color=Colors.GREEN))

    async def _receive_msgs(self, conn):
        while True:
            res = (await self._bot.loop.sock_recv(conn.sock, BUF_SIZE)).decode(ENCODING)
            if not res:
                continue

            msgs = res.split("\r\n")
            for msg in msgs:
                if "PING" in msg:
                    await self._bot.loop.sock_sendall(conn.sock, "PONG :tmi.twitch.tv\r\n".encode(ENCODING))

                try:
                    src, _, channel,    message = msg.split(" ", 3)
                except ValueError as e:
                    continue

                text = Text()
                text.add_component(text=f"[{channel.replace(':', '').replace('#', '')}-stream] ", color=Colors.DARK_GRAY)
                text.add_component(text=src.split("!", 1)[0].replace(":", ""), color=conn.color)
                text.add_component(text=" " + message.replace(":", ""), color=Colors.WHITE)

                for player in self.connections.get(conn.channel):
                    await player.server.send_message(text, player=player.player)

    # @tasks.loop(seconds=0.5)
    # async def _receive_msgs(self):
    #     for player in self._connected_players:
    #         res = (await self._bot.loop.sock_recv(player.channel, BUF_SIZE)).decode(ENCODING)
    #         if not res:
    #             continue
    #
    #         if "PING" in res:
    #             await self._bot.loop.sock_sendall(player.channel, "PONG".encode(ENCODING))
    #
    #         try:
    #             src, _, channel, message = res.split(" ", 3)
    #         except ValueError:
    #             continue
    #
    #
    #         text = Text()
    #         text.add_component(text=f"[{channel.replace(':', '').replace('#', '')}-stream] ", color=Colors.DARK_GRAY)
    #         text.add_component(text=src.split("!", 1)[0].replace(":", ""), color=player.color)
    #         text.add_component(text=" " + message.removesuffix("\r\n").replace(":", ""), color=Colors.WHITE)
    #
    #         await player.server.send_message(text, player=player.player)