from discord.ext import commands
from litebot.core.minecraft import MinecraftServer

def get_server(ctx: commands.Context, name: str) -> MinecraftServer:
    if name:
        return ctx.bot.servers[name]
    else:
        return ctx.bot.servers[ctx.channel.id]