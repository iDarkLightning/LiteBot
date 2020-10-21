import discord
from discord.ext import commands
from discord.utils import get
import json

bot = discord.Client()
with open('./modules/discord-utils/discord_config.json') as json_file:
    config = json.load(json_file)

class scalable_voice(commands.Cog):

    def __init__(self, bot):
        self.client = bot
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        
        category_id = config["scalable_voice"]["category_id"]
        add_channel_id = config["scalable_voice"]["add_channel_id"]
        guild = member.guild
        category = discord.utils.get(guild.categories, id=category_id)

        if after.channel and after.channel.id == add_channel_id:
            scalable_voice_number = (len(category.voice_channels)-1) +1

            channel = await guild.create_voice_channel(name=f'Scalable Voice {scalable_voice_number}', category=category)
            await member.move_to(channel)

        if before.channel and before.channel in category.voice_channels and not before.channel.members:
            if before.channel != discord.utils.get(guild.voice_channels, id=add_channel_id):
                await before.channel.delete()
def setup(bot):
    bot.add_cog(scalable_voice(bot))
