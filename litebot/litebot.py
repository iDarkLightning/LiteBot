import discord
from discord.ext import commands
from .minecraft.server_commands.core import ServerCommand
from .minecraft.server_commands.server_context import ServerContext
from .utils.config import MainConfig, ModuleConfig
from .utils.logging import get_logger
from .minecraft.server import MinecraftServer
import os, inspect

MODULES_PATH = "./modules"

class LiteBot(commands.Bot):
    VERSION = 3.0

    def __init__(self):
        self.config = MainConfig()
        self.module_config = ModuleConfig()
        super().__init__(
            command_prefix=commands.when_mentioned_or(*self.config["prefixes"]),
            help_command=None,
            intents=discord.Intents.all())
        self.logger = get_logger("bot")
        self._init_servers()

    def _init_servers(self):
        for server in self.config["servers"]:
            MinecraftServer(server, self, **self.config["servers"][server])

    def add_cog(self, cog: commands.Cog, required: bool = False) -> None:
        func_list = [getattr(cog, func) for func in dir(cog)]
        server_commands = [func for func in func_list if isinstance(func, ServerCommand)]

        for server_command in server_commands:
            server_command.cog = cog

        if required:
            super().add_cog(cog)
            self.logger.info(f"Loaded cog: {cog.__cog_name__}")
            return

        module = os.path.basename(
            os.path.normpath(os.path.split(os.path.relpath(inspect.getmodule(cog).__file__, MODULES_PATH))[0]))

        try:
            if self.module_config.cog_enabled(module, cog.__cog_name__):
                self.logger.info(f"Loaded cog: {cog.__cog_name__}")
                super().add_cog(cog)
        except ModuleNotFoundError:
            self.logger.warning(f"Tried to load cog: {cog.__cog_name__} for invalid module: {module}")

    async def dispatch_server_command(self, server, command, *args):
        command = ServerCommand.get_from_name(command)
        command_ctx = ServerContext(server, self)
        await command.invoke(command_ctx, args)

    async def on_ready(self):
        self.logger.info(f"{self.user.name} is now online!")

    def __repr__(self):
        return f"LiteBot: Version: {LiteBot.VERSION}"



