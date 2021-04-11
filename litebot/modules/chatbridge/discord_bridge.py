from discord.ext import commands
from discord import Message

from litebot.errors import ServerNotFound
from litebot.litebot import LiteBot
from litebot.minecraft import server_commands
from litebot.minecraft.server import MinecraftServer
from litebot.minecraft.server_commands.server_context import ServerEventContext


class DiscordBridge(commands.Cog):
    def __init__(self, bot: LiteBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        """
        Forwards a message from a bridge channel to the server
        :param message: The message that was sent
        :type message: discord.Message
        """
        try:
            server = MinecraftServer.get_from_channel(message.channel.id)
        except ServerNotFound:
            return

        if not message.author.bot:
            await server.send_discord_message(message)

    @server_commands.event(name="message")
    async def _server_message(self, ctx: ServerEventContext, message: str):
        """
        Forwards a message sent on a server to the bridge channel.
        If the server is connected to another server, then the connected bridge channel is used
        :param ctx: The context the event was executed in
        :type ctx: ServerEventContext
        :param message: The message sent
        :type message: str
        """
        server_bridge = self.bot.get_cog("ServerBridge")

        if not server_bridge:
            return await ctx.server.dispatch_message(message)

        matched_connections = list(filter(
            lambda s: s.player == ctx.player or s.origin_server == ctx.server, server_bridge.connections))

        if len(matched_connections) == 0:
            return await ctx.server.dispatch_message(message)

        for conn in matched_connections:
            await conn.send_discord_message(ctx.server, message)
