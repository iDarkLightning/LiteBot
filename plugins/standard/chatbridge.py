__plugin_meta__ = {
    "name": "Chat Bridge",
    "description": "Bridges chat from servers to a discord channel, and also between serversr",
    "authors": ["iDarkLightning"]
}

import re

import aiohttp
from discord import Message, Webhook, AsyncWebhookAdapter

from litebot.core import Cog
from litebot.core.minecraft import MinecraftServer, Text, Colors
from litebot.errors import ServerNotFound
from litebot.utils.requests import fetch


def _gen_config(bot):
    return {"webhook_urls": {s.name: "" for s in bot.servers.all}}

class ChatBridge(Cog):
    SKIN_AVATAR = "https://crafatar.com/avatars/"
    MOJANG_API = "https://sessionserver.mojang.com/session/minecraft/profile/"

    def __init__(self):
        self._uuid_name = {}

    @Cog.setting(name="Discord -> Server Bridge",
                 description="Forwards messages from the discord bridge channel to the server",
                 config={"message_format": "$player_name: "})
    @Cog.listener(type=Cog.ListenerTypes.DISCORD, name="on_message")
    async def _discord_server(self, setting, message: Message):
        try:
            server = self._bot.servers[message.channel.id]
        except ServerNotFound:
            return

        if not message.author.bot:
            await self._process_message(server, message, setting.config["message_format"])

    @Cog.setting(name="Server -> Discord Bridge",
                 description="Forwards messages from a server to its respective bridgee channel",
                 config=_gen_config)
    @Cog.listener(type=Cog.ListenerTypes.MINECRAFT, name="on_message")
    async def _server_discord(self, setting, payload):
        pfp = ChatBridge.SKIN_AVATAR + payload.player_uuid
        name = payload.player_name if payload.player_name else await self._get_name(payload)

        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(setting.config["webhook_urls"][payload.server.name], adapter=AsyncWebhookAdapter(session))
            await webhook.send(
                payload.message,
                username=name,
                avatar_url=pfp
            )

    async def _get_name(self, payload):
        if name := self._uuid_name.get(payload.player_uuid):
            return name

        res = await fetch(ChatBridge.MOJANG_API + payload.player_uuid)
        self._uuid_name[payload.player_uuid] = res["name"]
        return res["name"]

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

def setup(bot):
    bot.add_cog(ChatBridge())

