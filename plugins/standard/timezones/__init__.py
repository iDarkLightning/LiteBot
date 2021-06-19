__plugin_meta__ = {
    "name": "Timezones",
    "description": "Lets you view the timezone for different members on discord",
    "authors": ["iDarkLightning"]
}

from typing import Optional

import discord
import pytz
from discord.ext import commands
from datetime import datetime

from litebot.core import Cog
from litebot.utils import embeds
from litebot.utils.data_manip import split_string
from litebot.utils.menus import CodeBlockMenu

CHAR_LIMIT = 1500

class TimezoneCommand(Cog):
    @Cog.setting(name="Timezone Command",
                 description="Set a timezone and view the timezone of different members on discord!")
    @commands.group(name="timezone", aliases=["tz"])
    async def _timezone(self, ctx: commands.Context):
        """
        This is the root command for the timezone group.
        This command serves no function without
        a subcommand, but will send the help message for this group.
        Essentially invokes `help timezone`
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help("timezone")

    @_timezone.command(name="view")
    async def _timezone_view(self, ctx: commands.Context) -> None:
        """
        This command let's you view all the timezones
        """
        timezones = "\n".join(pytz.all_timezones)
        parts = split_string(timezones, CHAR_LIMIT)
        menu = CodeBlockMenu(parts)
        await menu.start(ctx)

    @_timezone.command("get")
    async def _timezone_get(self, ctx: commands.Context, member: discord.Member) -> None:
        """
        This command let's you view the timezone for a member.
        `member` The member's who's time you want to view
        """
        timezone_name = set([role.name for role in member.roles]) & set(pytz.all_timezones)
        if not timezone_name:
            return await ctx.send(embed=embeds.ErrorEmbed(f"{member} has not set up a timezone!"))

        timezone = pytz.timezone(next(iter(timezone_name)))
        embed = embeds.InfoEmbed(f"The time is: {datetime.now(timezone).strftime('%H:%M:%S')}")
        embed.set_author(name=member.display_name, icon_url=member.avatar_url).set_footer(
            text=f"Requested By: {ctx.author.name}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @_timezone.command("set")
    async def _timezone_set(self, ctx: commands.Context, zone: str) -> Optional[discord.Message]:
        """
        Let's you set your timezone.
        `zone` The timezone to set it to
        """
        if zone not in pytz.all_timezones:
            return await ctx.send(embed=embeds.ErrorEmbed("That timezone does not exist!"))

        cur_role = list(filter(lambda r: r.name == zone, ctx.guild.roles))
        if len(cur_role) == 0:
            cur_role = await ctx.guild.create_role(name=zone, mentionable=False)
        else:
            cur_role = cur_role[0]

        await ctx.author.remove_roles(*(
            role for role in ctx.author.roles if role.name in pytz.all_timezones))

        await ctx.author.add_roles(cur_role)
        await ctx.send(embed=embeds.SuccessEmbed(f"Your timezone has been set to {zone}"))

def setup(bot):
    bot.add_cog(TimezoneCommand())