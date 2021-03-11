import discord
from discord.ext import commands
from .minecraft.server_commands.core import ServerCommand
from .minecraft.server_commands.server_context import ServerContext
from .utils.config import MainConfig, ModuleConfig
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
        self._init_servers()

    def _init_servers(self):
        for server in self.config.servers:
            MinecraftServer(server, self, **self.config.servers[server])

    async def dispatch_server_command(self, server, command, *args):
        command = ServerCommand.get_from_name(command)
        command_ctx = ServerContext(server, self)
        await command.invoke(command_ctx, args)

    async def on_ready(self):
        self.logger.info(f"{self.user.name} is now online!")

    def __repr__(self):
        return f"LiteBot: Version: {LiteBot.VERSION}"



