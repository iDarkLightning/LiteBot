import discord
from discord.ext import commands
from discord.utils import get
import json
import requests
import re
import datetime
from datetime import datetime
import utils
import bot as main

bot = discord.Client()
config = main.config

with open('./commands/modules.json', 'r') as f:
    modules = json.loads(f.read())


class cog_loading(commands.Cog):

    def __init__(self, bot):
        self.client = bot

    @commands.command(brief="`load <cog_name>` loads a cog")
    @commands.has_permissions(administrator=True)
    async def load(self, ctx, extension):
        self.client.load_extension(f'commands.{extension}')
        modules[extension] = 'True'
        with open ('./commands/modules.json', 'w') as f:
            f.write(json.dumps(modules))
        await ctx.send(embed=discord.Embed(title=f'{extension} loaded'))

    @commands.command(brief='`unload <cog_name>` unloads a cog')
    @commands.has_permissions(administrator=True)
    async def unload(self, ctx, extension):
        self.client.unload_extension(f'commands.{extension}')
        modules[extension] = 'False'
        with open ('./commands/modules.json', 'w') as f:
            f.write(json.dumps(modules))
        await ctx.send(embed=discord.Embed(title=f'{extension} unloaded'))
    
    @commands.command(brief='`reload <cog_name>` reloads a cog')
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx, extension):
        try:
            self.client.unload_extension(f'commands.{extension}')
        except commands.ExtensionNotLoaded:
            await ctx.send(embed=discord.Embed(title=f'{extension} is not loaded', color=0xFF0000))
        else:
            self.client.load_extension(f'commands.{extension}')
            await ctx.send(embed=discord.Embed(title=f'{extension} reloaded'))

def setup(bot):
    bot.add_cog(cog_loading(bot))

