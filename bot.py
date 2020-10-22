import discord
from discord.ext import commands
from discord.utils import get
import json
import os
import time
import datetime
from datetime import datetime
import system.utils.modules_config

with open('config.json') as json_file:
    config = json.load(json_file)

with open('./modules.json') as json_file:
    modules = json.load(json_file)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config["prefix"], intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=config["prefix"] + "help"))

for filename in os.listdir('./system'):
    if os.path.isfile(f'./system/{filename}') and filename.endswith('.py'):
        bot.load_extension(f'system.{filename[:-3]}')

for filename in os.listdir('./modules'):
    if os.path.isdir(f'./modules/{filename}'):
        for module in os.listdir(f'./modules/{filename}'):
            if module.endswith('.py') and modules[filename][module[:-3]] == True:
                bot.load_extension(f'modules.{filename}.{module[:-3]}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(embed=discord.Embed(title='You do not have permission to execute this command', color=0xFF0000))
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send(embed=discord.Embed(title='This command was used improperly', color=0xFF0000))
    else:
        raise error

bot.run(config["token"])