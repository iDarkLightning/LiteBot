from discord.ext import commands
from litebot.core.converters import get_server
from litebot.utils import embeds


class TPSCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tps", aliases=["mspt"])
    async def _tps(self, ctx: commands.Context, server: str = None) -> None:
        """
        Allows you to view the TPS and MSPT of a server.
        You must include the server name unless the command is run in a bridge channel.
        Requires that the server is running carpet mod, and that the `script` command is enabled
        `server` The name of the server you wish to see the tps for
        """
        server = get_server(ctx, server)
        tps, mspt = server.tps()
        res_str = f"TPS: {tps} MSPT: {mspt}"

        if mspt <= 30:
            await ctx.send(embed=embeds.SuccessEmbed(res_str))
        elif 30 < mspt <= 50.0:
            await ctx.send(embed=embeds.WarningEmbed(res_str))
        elif mspt > 50:
            await ctx.send(embed=embeds.ErrorEmbed(res_str))