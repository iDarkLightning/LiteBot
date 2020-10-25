import discord
from discord.utils import get
from discord.ext import commands
import json

bot = discord.Client()
with open('./modules/discord-utils/discord_config.json') as json_file:
    config = json.load(json_file)

class auto_role(commands.Cog):
    
    def __init__(self, bot):
        self.client = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = get(member.guild.roles, id=(config["auto_role-id"]))
        await member.add_roles(role)

def setup(bot):
    bot.add_cog(auto_role(bot)) 