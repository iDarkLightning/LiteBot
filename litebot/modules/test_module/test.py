from discord.ext import commands

from litebot.minecraft.server_commands.core import server_command
from litebot.minecraft.server_commands.server_context import ServerContext


class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @server_command()
    async def test(self, ctx: ServerContext):
        await ctx.server.recieve_message("im not changing the code and restarting the bot and making the POST request again every time, wdym?")

    @commands.command()
    async def test(self, ctx: commands.Context):
        await ctx.send("test success")