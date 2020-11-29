from LiteBot import LiteBot
import json
import platform
from utils.utils import *

bot = LiteBot()
bot.init_modules()
bot.system_commands()

@bot.event
async def on_ready():
    print(bot.user)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(embed=discord.Embed(title='You do not have permission to execute this command', color=0xFF0000))
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send(embed=discord.Embed(title='This command was used improperly', color=0xFF0000))
    else:
        raise error

bot.run(bot.token)

