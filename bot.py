import discord
from discord.ext import commands

async def command_prefix(bot, message):
    prefixes = bot.config.get('prefixes', ['.'])
    prefixes.append(bot.user.mention)

    return prefixes

bot = commands.Bot(command_prefix=command_prefix)

bot.load_extension('utils.config')
bot.load_extension('utils.error_handling')
bot.load_extension('utils.cog_loader')

if __name__ == '__main__':
    bot.run(bot.config.get('token'))
