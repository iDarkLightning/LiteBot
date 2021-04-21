import re

from discord.ext import commands
from discord import Message

from litebot.errors import ServerNotFound
from litebot.litebot import LiteBot
from litebot.minecraft import server_commands
from litebot.minecraft.server import MinecraftServer
from litebot.minecraft.server_commands.server_context import ServerEventPayload
from litebot.minecraft.text import Text, Colors


class DiscordBridge(commands.Cog):
    def __init__(self, bot: LiteBot):
        self.bot = bot
        self.config = self.bot.module_config["chatbridge"]["config"]

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        """
        Forwards a message from a bridge channel to the server
        :param message: The message that was sent
        :type message: discord.Message
        """
        try:
            server = self.bot.servers.get_from_channel(message.channel.id)
        except ServerNotFound:
            return

        if not message.author.bot:
            await self._process_message(server, message)

    @server_commands.event(name="on_message")
    async def _server_message(self, payload):
        """
        Forwards a message sent on a server to the bridge channel.
        If the server is connected to another server, then the connected bridge channel is used
        :param ctx: The context the event was executed in
        :type ctx: ServerEventPayload
        :param message: The message sent
        :type message: str
        """
        server_bridge = self.bot.get_cog("ServerBridge")

        if not server_bridge:
            return await payload.server.recv_message(payload.message)

        matched_connections = list(filter(
            lambda s: s.player == payload.player or s.origin_server == payload.server, server_bridge.connections))

        if len(matched_connections) == 0:
            if not payload.player_name:
                return await payload.server.recv_message(payload.message)

            prefix, suffix = re.split("\\$player_name", self.config["incoming_messages"], 2)
            message = prefix + payload.player_name + suffix + payload.message
            return await payload.server.recv_message(message)

        for conn in matched_connections:
            await conn.send_discord_message(payload.server, payload.message)

    async def _process_message(self, server: MinecraftServer, message: Message) -> None:
        prefix, suffix = re.split("\\$player_name", self.config["outgoing_messages"], 2)
        text = Text().add_component(text=prefix)
        text.add_component(text=message.author.display_name, color=hex(message.author.color.value).replace("0x", "#"))

        text.add_component(text=suffix)

        if message.content:
            text.add_component(text=message.clean_content)

        if message.attachments:
            if message.content:
                text.add_component(text=" ")

            for attachement in message.attachments:
                text.add_component(
                    text=attachement.filename,
                    clickEvent={"action": "open_url", "value": attachement.url},
                    color=Colors.GREEN,
                    underlined=True,
                    hoverEvent={"action": "show_text", "value": "Click to open in your web browser"}
                )

        await server.send_message(text=text)