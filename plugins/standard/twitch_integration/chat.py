from random import randint

from litebot.core import Cog
from litebot.core.minecraft import ServerCommandContext, commands, Text, Colors
from plugins.standard.twitch_integration.client import TwitchClient, Connection, ConnectedPlayer, BUF_SIZE, ENCODING
from plugins.standard.twitch_integration.utils import ChannelSuggester, ConnectedChannelSuggester


class TwitchChat(Cog):
    def __init__(self, bot, plugin):
        self._config = plugin.config
        self._client = TwitchClient(bot.loop, self._config)
        self.channels = {}
        self.connections = {}

    @Cog.setting(name="Stream Command",
                 description="Stream the live chat of a twitch channel to your in game chat")
    @commands.command(name="stream")
    async def _stream(self, ctx: ServerCommandContext):
        """
        Namespace for declaring /stream subcommands
        """
        pass

    @_stream.sub(name="connect")
    async def _stream_connect(self, ctx: ServerCommandContext, channel: ChannelSuggester):
        task = self.channels.get(channel)

        if not task:
            sock = await self._client.connect(channel)

            if not sock:
                return await ctx.send(text=Text.error_message(
                    f"Could not connect to {channel}-stream! Maybe try again?"))

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