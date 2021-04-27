from discord.ext import commands

from litebot.core import Cog
from litebot.errors import ServerNotRunningCarpet
from litebot.utils.checks import role_checks
from litebot.modules.core.converters import get_server
from litebot.utils import embeds
import datetime
from datetime import datetime

class StatusCommand(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="status", aliases=["s", "online", "o"])
    @role_checks.config_role_check("members_role")
    async def _status(self, ctx: commands.Context, server: str = None) -> None:
        """
        Allows you to view the status of a server.
        You must include the server name unless the command is run in a bridge channel.
        `server` The name of the server you wish to see the status for
        """
        server = get_server(ctx, server)
        status = server.status()
        embed = embeds.SuccessEmbed(f"{server.name.upper()} Status") if \
            status.online else embeds.ErrorEmbed(f"{server.name.upper()} Status")

        embed.description = f"The server is currently {'online' if status.online else 'offline'}!"
        embed.timestamp = datetime.utcnow()

        if status.online:
            try:
                tps, mspt = server.tps()
                embed.add_field(name="TPS", value=str(mspt), inline=True)
                embed.add_field(name="MSPT", value=str(tps), inline=True)
            except ServerNotRunningCarpet:
                pass

            if len(status.players):
                embed.add_field(name=f"Online Players ({status.players.online}/{status.players.max})",
                                value=", ".join(status.players), inline=False)

        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f"Requested by: {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
