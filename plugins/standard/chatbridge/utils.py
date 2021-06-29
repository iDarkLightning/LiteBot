import re

from litebot.core.minecraft import MinecraftServer, Text, ServerCommandContext, Player, Colors
from litebot.core.minecraft.commands.arguments import StrictSuggester


class BridgeConnection:
    def __init__(self, source_server: MinecraftServer, connected_servers: list[MinecraftServer], player: Player):
        self.player = player
        self.source_server = source_server
        self.connected_servers = connected_servers

    def add_servers(self, servers):
        self.connected_servers = list({*self.connected_servers, *servers})
        return self

    async def send_bridge_message(self, name, payload, msg_format):
        prefix, suffix = re.split("\\$player_name", msg_format, 2)
        msg = Text().add_component(text=f"[{payload.server.name.upper()}] ",color=Colors.DARK_GRAY).add_component(
            text=prefix).add_component(text=name, color=Colors.GRAY).add_component(
            text=suffix, color=Colors.WHITE).add_component(text=payload.message, color=Colors.WHITE)

        if payload.server in self.connected_servers and payload.server is not self.source_server:
            await self.source_server.send_message(text=msg, player=self.player)

        for server in self.connected_servers:
            if server is not payload.server:
                await server.send_message(text=msg)

class ServerSuggester(StrictSuggester):
    async def suggest(self, ctx: ServerCommandContext) -> list:
        return [s.name for s in ctx.bot.servers if s is not ctx.server and s.connected]