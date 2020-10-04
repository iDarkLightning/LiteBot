import discord
from discord.ext import commands
from discord.utils import get
import json
import os
import time
import datetime
from datetime import datetime

with open('config.json') as json_file:
    config = json.load(json_file)

with open('./commands/modules.json') as json_file:
    modules = json.load(json_file)

bot = commands.Bot(command_prefix=config["prefix"])
bot.remove_command('help')

@bot.event
async def on_ready():
    print("{} is online".format(bot.user.name))
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=config["prefix"] + "help"))

for filename in os.listdir('./commands'):
    if filename.endswith('.py') and modules[filename[:-3]] == 'True':
        bot.load_extension(f'commands.{filename[:-3]}')
for filename in os.listdir('./'):
    if filename in ['help_command.py', 'cog_loading.py']:
        bot.load_extension(f'{filename[:-3]}')

@bot.command(brief="`.ping` or `.pong` Returns the bot's latency to discord", aliases=['ping', 'pong'])
async def latency(ctx):
    before = time.time()

    message = await ctx.send(embed=discord.Embed(
        title='Checking Latency',
        colour=discord.Colour.blue(),
        timestamp=datetime.now())
        .set_footer(text='{0.display_name}#{0.discriminator}'.format(ctx.author), icon_url=ctx.author.avatar_url))

    after = time.time()

    latency = after - before

    await message.edit(embed=discord.Embed(
        title='Latency',
        colour=(0xADD8E6),
        timestamp=datetime.now())
        .add_field(name='WebSocket Latency', value='{0:.2f}ms'.format(bot.latency * 1000))
        .add_field(name='HTTP Latency', value='{0:.2f}ms'.format(latency * 1000))
        .set_footer(text='{0.display_name}#{0.discriminator}'.format(ctx.author), icon_url=ctx.author.avatar_url))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(embed=discord.Embed(title='You do not have permission to execute this command', color=0xFF0000))    
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send(embed=discord.Embed(title='This command was used improperly', color=0xFF0000))
    else:
        raise error

bot.run(config["token"])
