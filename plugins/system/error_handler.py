from datetime import datetime

from discord.ext.commands import CommandError, CommandInvokeError, MissingRequiredArgument, CheckFailure

from litebot.core import Cog
from litebot.core.context import Context
from litebot.errors import ServerNotFound, ServerConnectionFailed
from litebot.utils.embeds import ErrorEmbed
from litebot.utils.fmt_strings import CODE_BLOCK

LINE_BREAK = "\n"
ISSUE_URL = "https://github.com/iDarkLightning/LiteBot/issues"

class ErrorHandler(Cog, required=True):
    @Cog.listener(type=Cog.ListenerTypes.DISCORD)
    async def on_command_error(self, ctx: Context, error: CommandError):
        embed = ErrorEmbed("", timestamp=datetime.utcnow())
        embed.set_author(name="Uh oh!")
        embed.set_footer(
            text=f"Error Caused By: {ctx.author.display_name}",
            icon_url=ctx.author.avatar_url
        )
        embed.add_field(
            name="Unexpected Behaviour?",
            value=f"Reach out to your server administrator or create an issue [here]({ISSUE_URL})"
        )

        if isinstance(error, CommandInvokeError):
            if isinstance(error.original, ServerNotFound):
                embed.title = "No server found with that name!"
                embed.description = f"Perhaps you meant:\n{CODE_BLOCK.format('', LINE_BREAK.join([s.name for s in self._bot.servers]))}"
                return await ctx.send(embed=embed)
            if isinstance(error.original, ServerConnectionFailed):
                embed.title = "Connecting to that server failed!"
                embed.description = "Try checking if the server is currently online or contact your system administrator"
                return await ctx.send(embed=embed)
        elif isinstance(error, MissingRequiredArgument):
            embed.title = "Missing Required Argument!"
            embed.description = f"Name: `{error.param.name}`, Type: `{error.param.annotation}`"
            return await ctx.send(embed=embed)
        elif isinstance(error, CheckFailure):
            embed.title = "You do not have permission to perform this command!"
            return await ctx.send(embed=embed)
        else:
            embed.title = "An unexpected error occured!"
            embed.description = CODE_BLOCK.format("", error)
            return await ctx.send(embed=embed)