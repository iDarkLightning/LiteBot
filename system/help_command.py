import discord
from discord.ext import commands
from discord.utils import get
import json
import requests
import re
import datetime
from datetime import datetime
import system.utils.utils as utils
import bot as main

bot = discord.Client()

config = main.config

class help_command(commands.Cog):

    def __init__(self, bot):
        self.client = bot

    @commands.command(brief='`help` displays this panel')
    async def help(self, ctx, command_help=None):
        embed = discord.Embed(title='LiteBot Help Panel', color=0xADD8E6, timestamp=datetime.utcnow())
        if command_help!= None:
            for command in self.client.commands:
                if command_help == command.name:
                    command_help = command
                    embed.add_field(name=f'{str(command).capitalize()} Command', value=f'{command.help}', inline=False)
        else:
            for command in self.client.commands:
                if command.checks:
                    try:
                        if command.checks[0](ctx) == True:
                            embed.add_field(name=f'{str(command).capitalize()} Command', value=f'{command.brief}', inline=False)
                    except:
                        pass       
                else:
                    embed.add_field(name=f'{str(command).capitalize()} Command', value=f'{command.brief}', inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(help_command(bot))
