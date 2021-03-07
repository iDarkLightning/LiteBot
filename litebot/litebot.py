import discord
from discord.ext import commands
from .utils.config import MainConfig, ModuleConfig

class LiteBot(commands.Bot):
    VERSION = 3.0

    def __init__(self):
        self.config = MainConfig()
        self.module_config = ModuleConfig()
        super().__init__(
            command_prefix=commands.when_mentioned_or(*self.config.prefixes),
            help_command=None,
            intents=discord.Intents.all())

    def __repr__(self):
        return f"LiteBot: Version: {LiteBot.VERSION}"
