import discord
from discord.ext import commands

class CogLoader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load(self, cog, cog_name=None):
        if not cog_name:
            if not hasattr(cog, 'COG_NAME'):
                raise AttributeError('Cog is missing a COG_NAME attribute')

            cog_name = cog.COG_NAME

        module_configs = self.bot.config.modules
        cog_config = module_configs.get(cog_name)

        if cog_config['enabled']:
            cog.config = cog_config['config']
            self.bot.add_cog(cog)

            cog.on_cog_load()

def setup(bot):
    bot.cog_loader = CogLoader(bot)
