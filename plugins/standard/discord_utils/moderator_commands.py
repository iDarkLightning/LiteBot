from discord.ext import commands

from litebot.core import Cog, Optional


class ModeratorCommands(Cog):
    @Cog.setting(name="Clear Command", description="Delete the given amount of messages from the chat")
    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def _clear(self, ctx: commands.Context, amount: Optional[int] = 5) -> None:
        """
        Deletes the the given amount of messages in the channel.
        If no amount is given, it will default to 5.
        `amount`: The amount of messages to delete
        """
        await ctx.channel.purge(limit=amount + 1)