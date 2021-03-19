from discord.ext import commands
from litebot.errors import ServerNotFound
from litebot.minecraft.server import MinecraftServer

def get_server(ctx: commands.Context, name: str) -> MinecraftServer:
    if name:
        return MinecraftServer.get_from_name(name)
    else:
        name = filter(lambda s: s.bridge_channel_id == ctx.channel.id, MinecraftServer.get_all_instances())
        try:
            return list(name)[0]
        except IndexError:
            raise ServerNotFound

