import re
from typing import Optional

import discord
from discord.ext import commands

from litebot.core import Cog
from litebot.utils.data_manip import split_string
from litebot.utils.embeds import InfoEmbed
from litebot.utils.menus import DescriptionMenu
from plugins.standard.discord_utils.utils import RoleConverter

CHAR_LIMIT = 250

class ListCommand(Cog):
    @Cog.setting(name="List Command", description="List all the members with a role on discord")
    @commands.command(name="list")
    async def _list(self, ctx: commands.Context, *, role: Optional[RoleConverter] = None) -> None:
        """
        View what people are in a role.
        If no role is specified, it will instead show how many people are in each role.
        `role` The role to view members for.
        """
        if not role:
            await self._display_role_counts(ctx)
        else:
            await self._display_role_members(ctx, role)

    async def _display_role_counts(self, ctx: commands.Context) -> None:
        """
        Displays all the roles in the server, and how many people are in each role.
        :param ctx: The context that the comand is executed in
        :type ctx: commands.Context
        """
        res_str = [f"{role.mention}: {len(role.members)}" for role in ctx.guild.roles]

        await ctx.send(embed=InfoEmbed(
            f"There are {len(ctx.guild.members)} members on this server", description="\n".join(res_str)))

    async def _display_role_members(self, ctx: commands.Context, roles: list[discord.Role]):
        """
        Displays all the members in a role.
        :param ctx: The context that the comand is executed in
        :type ctx: commands.Context
        """
        members = [role.members for role in roles][0]
        members_names = sorted([member.name.replace("_", "\\_") for member in members], key=str.lower)

        title_str = f"There are {len(members)} with role: {roles[0].name}"

        if len("\n".join(members_names)) >= CHAR_LIMIT:
            parts = split_string("\n".join(members_names), CHAR_LIMIT)
            await DescriptionMenu(parts, title_str).start(ctx)
        else:
            await ctx.send(embed=InfoEmbed(title_str, description="\n".join(members_names)))