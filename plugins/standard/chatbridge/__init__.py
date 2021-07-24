__plugin_meta__ = {
    "name": "Chat Bridge",
    "description": "Bridges chat from servers to a discord channel, and also between serversr",
    "authors": ["iDarkLightning"]
}

import re
from itertools import chain
from typing import Optional

import aiohttp
from discord import Message, Webhook, AsyncWebhookAdapter, AllowedMentions

from litebot.core import Cog
from litebot.core.minecraft import MinecraftServer, Text, Colors, commands, ServerCommandContext, ServerEventContext, \
    RPCContext
from litebot.core.minecraft.commands.arguments import MessageArgumentType
from litebot.core.minecraft.commands.payload import MessagePayload
from litebot.core.minecraft.rpc import rpc
from litebot.errors import ServerNotFound
from plugins.standard.chatbridge.utils import ServerSuggester, BridgeConnection


def _gen_config(bot):
    return {"webhook_urls": {s.name: "" for s in bot.servers.all}}

class ChatBridge(Cog):
    SKIN_AVATAR = "https://crafatar.com/avatars/"
    MOJANG_API = "https://sessionserver.mojang.com/session/minecraft/profile/"

    def __init__(self, bot, plugin):
        self._uuid_name = {}
        self._connections = {}
        self._config = plugin.config

    @Cog.setting(name="Discord -> Server Bridge",
                 description="Forwards messages from the discord bridge channel to the server")
    @Cog.listener(type=Cog.ListenerTypes.DISCORD, name="on_message")
    async def _discord_server(self, setting, message: Message):
        try:
            server = self._bot.servers[message.channel.id]
        except ServerNotFound:
            return

        if not message.author.bot:
            await self._process_message(server, message, self._config["message_format"])

    @Cog.setting(name="Server -> Discord Bridge",
                 description="Forwards messages from a server to its respective bridgee channel",
                 config=_gen_config)
    @Cog.listener(type=Cog.ListenerTypes.MINECRAFT, name="on_message")
    async def _server_discord(self, ctx: ServerEventContext, payload: MessagePayload):
        pfp = ChatBridge.SKIN_AVATAR + ctx.player.uuid
        name = ctx.player.name

        for connection in self._connections.values():
            await connection.send_bridge_message(name, payload, self._config["message_format"])

        servers = list(chain.from_iterable([*(s.connected_servers for s in self._connections.values())])) or [ctx.server]

        mentions = re.findall("@([^ ]+)", payload.message)
        members = []
        for mention in mentions:
            member = self._fetch_member(ctx, mention)
            if isinstance(member, str):
                continue

            members.append(member)
            payload.message = payload.message.replace(f"@{mention}", self._fetch_member(ctx, mention).mention)

        for server in servers:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(ctx.setting.config["webhook_urls"][server.name], adapter=AsyncWebhookAdapter(session))
                await webhook.send(
                    payload.message,
                    username=name,
                    avatar_url=pfp,
                    allowed_mentions=AllowedMentions(users=members, roles=False, everyone=False)
                )

    @Cog.setting(name="Server <-> Server Bridge",
                 description="Lets you create a bridge between servers, allowing for cross-server communication!")
    @commands.command(name="bridge")
    async def _bridge_command(self, ctx: ServerCommandContext) -> None:
        pass

    @_bridge_command.sub(name="send")
    async def _bridge_player_send(self, ctx: ServerCommandContext, server_name: ServerSuggester, message: MessageArgumentType):
        """
        Send a single message to another server
        """
        server = self._bot.servers[server_name]

        msg = Text().add_component(text=f"[{ctx.server.name}] ", color=Colors.GRAY).add_component(
            text=message, color=Colors.WHITE)

        await server.send_message(text=msg)

    @_bridge_command.sub(name="connect")
    async def _bridge_player_connect(self, ctx: ServerCommandContext, server_name: Optional[ServerSuggester]):
        """
        Connect to a server
        """
        try:
            servers = [self._bot.servers[server_name]]
        except (TypeError, ServerNotFound):
            servers = [s for s in self._bot.servers.all if s is not ctx.server]

        self._connections[ctx.player.uuid] = self._connections.get(ctx.player.uuid, BridgeConnection(
            ctx.server, servers, ctx.player
        )).add_servers(servers)

        await ctx.send(text=Text().add_component(
            text=f"You are now connected to {', '.join([s.name for s in self._connections[ctx.player.uuid].connected_servers])}",
            color=Colors.GREEN))

    @_bridge_command.sub(name="disconnect")
    async def _bridge_player_disconnect(self, ctx: ServerCommandContext):
        """
        Disconnect from a server
        """
        try:
            del self._connections[ctx.player.uuid]
            await ctx.send(text=Text().add_component(text="Disconnected from bridge connections", color=Colors.GREEN))
        except KeyError:
            await ctx.send(text=Text.error_message("You do not have any active bridge connections!"))

    @rpc(name="mentions")
    async def _fetch_mentions(self, ctx: RPCContext):
        return [f"@{m.name}" for m in ctx.server.bridge_channel.members]

    async def _process_message(self, server: MinecraftServer, message: Message, msg_format: str):
        prefix, suffix = re.split("\\$player_name", msg_format, 2)
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

    def _fetch_member(self, ctx, str_: str):
        members = ctx.server.bridge_channel.members
        for member in members:
            if member.display_name == str_ or member.name == str_:
                return member

        return "@" + str_

def setup(bot):
    bot.add_cog(ChatBridge)

def config(bot):
    return {
        "message_format": "$player_name: "
    }

