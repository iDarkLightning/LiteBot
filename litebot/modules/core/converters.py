from discord.ext import commands
from litebot.minecraft.server import MinecraftServer

def get_server(ctx: commands.Context, name: str) -> MinecraftServer:
    if name:
        return ctx.bot.servers.get_from_name(name)
    else:
        return ctx.bot.servers.get_from_channel(ctx.channel.id)