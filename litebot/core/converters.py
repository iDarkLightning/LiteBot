from discord.ext import commands
from litebot.minecraft.server import MinecraftServer

def get_server(ctx: commands.Context, name: str) -> MinecraftServer:
    if name:
        return MinecraftServer.get_from_name(name)
    else:
        return MinecraftServer.get_from_channel(ctx.channel.id)