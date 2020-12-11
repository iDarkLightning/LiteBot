from utils.utils import *

class ScalableVoice(commands.Cog):
    COG_NAME = 'utils.scalable_voice'
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        category_id = self.config["category_id"]
        add_channel_id = self.config["add_channel_id"]
        
        guild = member.guild
        category = discord.utils.get(guild.categories, id=category_id)

        if after.channel and after.channel.id == add_channel_id:
            scalable_voice_number = (len(category.voice_channels) - 1) + 1

            channel = await guild.create_voice_channel(name=f'Scalable Voice {scalable_voice_number}',
                                                       category=category)
            await member.move_to(channel)

        if before.channel and before.channel in category.voice_channels and not before.channel.members:
            if before.channel != discord.utils.get(guild.voice_channels, id=add_channel_id):
                await before.channel.delete()
