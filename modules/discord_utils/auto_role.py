from utils.utils import *


class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        self.config = self.client.module_config['discord_utils']['config']

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = get(member.guild.roles, id=(self.config["auto_role_id"]))
        await member.add_roles(role)
