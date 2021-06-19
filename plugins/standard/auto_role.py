__plugin_meta__ = {
    "name": "Auto Role",
    "description": "Automatically give a member a role upon join!",
    "authors": ["iDarkLightning"]
}

import discord

from discord.utils import get
from litebot.core import Cog


class AutoRole(Cog):
    @Cog.setting(name="Auto Role",
                 description="Automatically give a member a role upon join!",
                 config={"role_id": 0})
    @Cog.listener(type=Cog.ListenerTypes.DISCORD)
    async def on_member_join(self, setting, member: discord.Member) -> None:
        """
        Assigns a user the role set in the config when they join the guild.
        :param member: The member that joined
        :type member: discord.Member
        """
        role = get(member.guild.roles, id=setting.config["role_id"])
        await member.add_roles(role)

def setup(bot):
    bot.add_cog(AutoRole())