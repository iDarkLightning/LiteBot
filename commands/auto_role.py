import discord
from discord.utils import get
from discord.ext import commands
import bot as main

bot = discord.Client()
config = main.config

class auto_role(commands.Cog):
    
    def __init__(self, bot):
        self.client = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = get(member.guild.roles, id=(int(config["auto_role"])))
        await member.add_roles(role)

def setup(bot):
    bot.add_cog(auto_role(bot)) 