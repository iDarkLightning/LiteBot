import discord
from discord.ext import commands
from discord.utils import get
import json
import re
import os
import datetime
from datetime import datetime
import bot as main

bot = discord.Client()
config = main.config

with open('./modules.json', 'r') as f:
    modules = json.loads(f.read())

class cog_loading(commands.Cog):

    def __init__(self, bot):
        self.client = bot

    @commands.command(brief="`load <cog_name>` loads a cog")
    @commands.has_permissions(administrator=True)
    async def load(self, ctx, extension):
        for filename in os.listdir('./modules'):
            if os.path.isdir(f'./modules/{filename}'):
                for module in os.listdir(f'./modules/{filename}'):
                    if module.endswith('.py'):
                        if module[:-3] == extension:
                            try:
                                self.client.load_extension(f'modules.{filename}.{extension}')
                                modules[filename][extension] = True
                                with open ('./modules.json', 'w') as f:
                                    f.write(json.dumps(modules, sort_keys=True, indent=4, separators=(',', ':')))
                                await ctx.send(embed=discord.Embed(title=f'{extension} has now been loaded', color=0x32CD32))
                            except commands.ExtensionAlreadyLoaded:
                                await ctx.send(embed=discord.Embed(title=f'{extension} is already loaded', color=0xFF0000))
    
    @commands.command(brief="`unload <cog_name>` unloads a cog")
    @commands.has_permissions(administrator=True)
    async def unload(self, ctx, extension):
        for filename in os.listdir('./modules'):
            if os.path.isdir(f'./modules/{filename}'):
                for module in os.listdir(f'./modules/{filename}'):
                    if module.endswith('.py'):
                        if module[:-3] == extension:
                            try:
                                self.client.unload_extension(f'modules.{filename}.{extension}')
                                modules[filename][extension] = False
                                with open ('./modules.json', 'w') as f:
                                    f.write(json.dumps(modules, sort_keys=True, indent=4, separators=(',', ':')))
                                await ctx.send(embed=discord.Embed(title=f'{extension} has now been unloaded', color=0x32CD32))
                            except commands.ExtensionNotLoaded:
                                await ctx.send(embed=discord.Embed(title=f'{extension} is not loaded', color=0xFF0000))

    @commands.command(brief="`reload <cog_name>` reloads a cog")
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx, extension):
        for filename in os.listdir('./modules'):
            if os.path.isdir(f'./modules/{filename}'):
                for module in os.listdir(f'./modules/{filename}'):
                    if module.endswith('.py'):
                        if module[:-3] == extension:
                            try:
                                self.client.unload_extension(f'modules.{filename}.{extension}')
                                self.client.load_extension(f'modules.{filename}.{extension}')
                                await ctx.send(embed=discord.Embed(title=f'{extension} has been reloaded', color=0x32CD32))
                            except commands.ExtensionNotLoaded:
                                await ctx.send(embed=discord.Embed(title=f'{extension} is not loaded', color=0xFF0000))

def setup(bot):
    bot.add_cog(cog_loading(bot))

