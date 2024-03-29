from typing import Optional

import discord
import jwt
from discord.ext import commands

from litebot.core import Cog
from litebot.utils import embeds
from litebot.utils.markdown import CODE_BLOCK


class TokenCommand(Cog, required=True):
    @commands.command(name="token")
    @commands.has_permissions(manage_guild=True)
    async def _token(self, ctx: commands.Context, member: Optional[discord.Member] = None) -> None:
        """
        Use this command to generate a JWT token to use with the bot's API.
        `member` An optional member parameter, if you would like to generate the token for someone else
        """
        user: discord.Member = member if member else ctx.message.author
        token = jwt.encode(
            {
                "user": user.id
            },
            self._bot.config["api_secret"],
            algorithm="HS256"
        )

        embed = embeds.InfoEmbed("Your token is: ", description=CODE_BLOCK.format("ini", f"[{token}]"))
        embed.add_field(
            name="Usage",
            value=f"Include the token in your headers with the `Authorization` key. You can view the API docs for more details.")
        embed.set_footer(
            text=f"Please keep this token secret. If you ever accidentally release this, please contact the bot owner to invalidate the token (change the secret)")
        await user.send(embed=embed)