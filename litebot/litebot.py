import discord
from discord.ext import commands
from .utils.config import MainConfig, ModuleConfig, ConfigMap
from .utils.logging import get_logger
from .minecraft.server import MinecraftServer

class LiteBot(commands.Bot):
    VERSION = 3.0

    def __init__(self):
        self.config = MainConfig()
        self.module_config = ModuleConfig()
        super().__init__(
            command_prefix=commands.when_mentioned_or(*self.config.prefixes),
            help_command=None,
            intents=discord.Intents.all())
        self.logger = get_logger("bot")
        self.servers = self.init_servers()

    def init_servers(self):
        servers = []
        for server in self.config.servers:
            servers.append(MinecraftServer(server, **self.config.servers[server]))
        return servers

    def __repr__(self):
        return f"LiteBot: Version: {LiteBot.VERSION}"

