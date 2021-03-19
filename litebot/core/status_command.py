from discord.ext import commands
from litebot.core.converters import get_server
from litebot.errors import ServerNotFound
from litebot.utils import embeds
import datetime
from datetime import datetime

class StatusCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="status", aliases=["s", "online", "o"])
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
        embed.timestamp = datetime.utcnow()

        if status.online:
            embed.add_field(name="Status", value="Online")
            embed.add_field(name="Players Online", value=f"{status.players.online}/{status.players.max}")
            embed.add_field(name="Online Players", value=", ".join(status.players), inline=False)
        else:
            embed.add_field(name="Status", value="Offline")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=ctx.message.guild)

        await ctx.send(embed=embed)