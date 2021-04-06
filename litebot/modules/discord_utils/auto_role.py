import discord
from discord.ext import commands
from discord.utils import get


class AutoRole(commands.Cog):
    def __init__(self, bot, module):
        self.bot = bot
        self.config = self.bot.module_config[module]["config"]

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """
        Assigns a user the role set in the config when they join the guild.
        :param member: The member that joined
        :type member: discord.Member
        """
        role = get(member.guild.roles, id=self.config["auto_role_id"])
        await member.add_roles(role)