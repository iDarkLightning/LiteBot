import copy
from typing import Union

from discord import User, Member
from discord.ext import commands

from litebot.core import Cog, Context


class AdminCommands(Cog, required=True):

    @commands.command(name="sudo", hidden=True)
    @commands.has_permissions(administrator=True)
    async def _sudo(self, ctx: Context, who: Union[Member, User], *, command: str):
        msg = copy.copy(ctx.message)
        msg.author = who
        msg.content = ctx.prefix + command
        new_ctx = await self._bot.get_context(msg, cls=type(ctx))
        await self._bot.invoke(new_ctx)
