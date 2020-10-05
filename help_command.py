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

class help_command(commands.Cog):

    def __init__(self, bot):
        self.client = bot

    @commands.command(brief='`help` displays this panel')
    async def help(self, ctx):
        embed = discord.Embed(title='LiteBot Help Panel', color=0xADD8E6, timestamp=datetime.utcnow())
        if ctx.message.author.guild_permissions.administrator:
            for command in self.client.commands:
                embed.add_field(name=f'{str(command).capitalize()} Command', value=f'{command.brief}', inline=False)
        else:
            if ctx.message.author.guild_permissions.manage_messages:
                for command in self.client.commands:
                    if str(command) not in ['unload', 'reload', 'load']:
                        utils.help_embed(embed, command, ctx)                    
            else:
                for command in self.client.commands:
                    if str(command) not in ['unload', 'reload', 'load', 'clear']:
                        utils.help_embed(embed, command, ctx)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(help_command(bot))
