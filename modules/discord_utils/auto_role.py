from utils.utils import *

class AutoRole(commands.Cog):
    COG_NAME = 'utils.auto_role'

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not hasattr(self.config, 'role_ids'):
            return
        
        for role in member.guild.roles:
            if role.id in self.config['role_ids']:
                await member.add_roles(role, reason='Auto-Role')
