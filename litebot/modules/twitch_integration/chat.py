from random import randint

import discord

from litebot.core import Cog
from litebot.core.minecraft import commands
from litebot.litebot import LiteBot
from litebot.core.minecraft import StrictSuggester, Suggester
from litebot.core.minecraft import ServerCommandContext
from litebot.core.minecraft.text import Text, Colors
from litebot.modules.twitch_integration.client import TwitchClient, BUF_SIZE, ENCODING, Connection, ConnectedPlayer


class ConnectedChannelSuggester(StrictSuggester):
    """
    A strict suggester for the /stream disconnect command.
    Suggests the channels that the player is currently connected to, and ensures that they do not attempt to
    disconnect from a channel that they aren't connected to.
    """
    async def suggest(self, ctx: ServerCommandContext, arg: str, prior_args: dict) -> list:
        chat_cog = ctx.bot.get_cog("TwitchChat")
        to_suggest = []

        for channel in chat_cog.channels:
            connections = chat_cog.connections[channel]
            if ctx.player.uuid in [c.player.uuid for c in connections]:
                to_suggest.append(channel)

        return to_suggest

class ChannelSuggester(Suggester):
    """
    A suggester for the /stream connect command.
    Suggests channels that other members on the server are currently connected to, or the channel of any members who
    might be currently streaming on twitch.
    """
    async def suggest(self, ctx: ServerCommandContext, arg: str, prior_args: dict) -> list:
        chat_cog = ctx.bot.get_cog("TwitchChat")
        guild = await ctx.bot.guild()
        streams = list(filter(lambda n: n is not None,map(
            self.get_stream_name, filter(lambda m: any([isinstance(a, discord.Streaming) for a in m.activities]),
                           sum([role.members for role in [guild.get_role(r) for r in ctx.bot.config["members_role"]]],
                               [])))))

        streams.extend(chat_cog.channels.keys())
        current_connections = []

        for channel in chat_cog.channels:
            connections = chat_cog.connections[channel]
            if ctx.player.uuid in [c.player.uuid for c in connections]:
                current_connections.append(channel)

        return list(set([s for s in streams if s not in current_connections]))

    def get_stream_name(self, member: discord.Member):
        streaming_activity = list(filter(lambda a: isinstance(a, discord.Streaming), member.activities))[0]

        if streaming_activity.platform == "Twitch":
            return streaming_activity.twitch_name

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
    async def _stream_connect(self, ctx: ServerCommandContext, channel: ChannelSuggester):
        """
        Connects you to the stream chat for a twitch streamer!
        `channel` The name of the channel to connect you to
        """
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

    @_stream.sub(name="disconnect")
    async def _stream_disconnect(self, ctx: ServerCommandContext, channel: ConnectedChannelSuggester):
        """
        Disconnects you from a connected stream
        """
        self.connections[channel] = list(filter(lambda c: c.player.uuid != ctx.player.uuid, self.connections[channel]))

        if not len(self.connections[channel]):
            task = self.channels[channel]
            task.cancel()

            del self.channels[channel]

        await ctx.send(text=Text().add_component(text=f"Disconnected from {channel}-stream!", color=Colors.GREEN))

    async def _receive_msgs(self, conn: Connection):
        """
        An async task to continuously receive and process messages from the connected channel
        :param conn: The connected channel
        :type conn: Connection
        """
        while True:
            res = (await self._bot.loop.sock_recv(conn.sock, BUF_SIZE)).decode(ENCODING)

            if res:
                await self._client.process_message(res, conn, self.connections.get(conn.channel))

