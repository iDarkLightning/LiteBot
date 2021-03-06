from utils.utils import *

class Streaming(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = self.client.module_config['discord_utils']['streaming']
        self.activity_types = None

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        activity_types = None
        streaming_role = get(after.guild.roles, id=self.config['streaming_role'])

        try:
            activity_types = after.activities
        except:
            ...

        #print(activity_types, after.name)
        if any(isinstance(a, discord.Streaming) for a in activity_types):
            if streaming_role not in after.roles and check_role(after, self.config['to_give_roles']):
                await after.add_roles(streaming_role)
                if self.config['announcements_channel'] != 1:
                    announcements_channel = get(after.guild.text_channels, id=self.config['announcements_channel'])
                    await announcements_channel.send(
                        f"Would you look at that! {after.mention} is streaming on {after.activity.platform}\n**{after.activity.name}**\nGo check them out!\n{after.activity.url}"
                    )
        else:
            ...
            # if streaming_role in after.roles:
            #     await after.remove_roles(streaming_role)
