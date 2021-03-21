import importlib
import discord
from async_property import async_property
from discord.ext import commands

from .errors import ServerNotFound
from .minecraft.server_commands.core import ServerCommand
from .minecraft.server_commands.server_context import ServerContext
from .utils import embeds
from .utils.config import MainConfig, ModuleConfig
from .utils.logging import get_logger
from .minecraft.server import MinecraftServer
import os
from .utils.fmt_strings import MODULE_LOADING, MODULE_PATH
from .system.help_command import HelpCommand

MODULES_PATH = "litebot/modules"
REQUIRED_MODULES = (
    "litebot.system",
    "litebot.core"
)

class LiteBot(commands.Bot):
    VERSION = 3.0

    def __init__(self):
        self.config = MainConfig()
        self.module_config = ModuleConfig()
        super().__init__(
            command_prefix=commands.when_mentioned_or(*self.config["prefixes"]),
            help_command=HelpCommand(),
            intents=discord.Intents.all())
        self.logger = get_logger("bot")
        self._initialising = False
        self._cur_module = None
        self._init_servers()

    def _init_servers(self):
        for server in self.config["servers"]:
            MinecraftServer(server, self, **self.config["servers"][server])

    @async_property
    async def log_channel(self):
        return await self.fetch_channel(self.config["log_channel_id"])

    @async_property
    async def guild(self):
        await self.wait_until_ready()
        return self.get_guild(self.config["main_guild_id"])


    def add_cog(self, cog: commands.Cog, required: bool = False) -> None:
        if self._initialising and not required:
            self.module_config.register_cog(self._cur_module, cog.__cog_name__)

        func_list = [getattr(cog, func) for func in dir(cog)]
        server_commands = [func for func in func_list if isinstance(func, ServerCommand)]

        for server_command in server_commands:
            server_command.cog = cog

        if required:
            super().add_cog(cog)
            self.logger.info(f"Loaded cog: {cog.__cog_name__}")
            return

        try:
            if self.module_config.cog_enabled(self._cur_module, cog.__cog_name__):
                self.logger.info(f"Loaded cog: {cog.__cog_name__}")
                super().add_cog(cog)
        except ModuleNotFoundError:
            self.logger.warning(f"Tried to load cog: {cog.__cog_name__} for invalid module: {self._cur_module}")

    def init_modules(self):
        for module in REQUIRED_MODULES:
            self.logger.info(MODULE_LOADING.format("Loading", module))
            super().load_extension(module)
            self.logger.info(MODULE_LOADING.format("Loaded", module))

        modules = filter(lambda path: os.path.isdir(os.path.join(MODULES_PATH, path))
                                      and path != "__pycache__", os.listdir(os.path.join(os.getcwd(), MODULES_PATH)))

        for module in modules:
            spec = importlib.util.find_spec(MODULE_PATH.format(module))
            lib = importlib.util.module_from_spec(spec)

            try:
                spec.loader.exec_module(lib)
            except Exception as e:
                self.logger.exception(e, exc_info=e)

            self._cur_module = module
            if hasattr(lib, "config"):
                config = getattr(lib, "config")(self)
                self.module_config.match_module(module, config)
            else:
                if module not in self.module_config:
                    self.module_config.register_module(module)

            enabled = self.module_config[module]["enabled"]
            if not enabled and not self.module_config[module].get("cogs"):
                self._initialising = True
                super().load_extension(MODULE_PATH.format(module))
                self._initialising = False
                return

            if hasattr(lib, "requirements"):
                requirements = getattr(lib, "requirements")
                if requirements(self) and enabled:
                    self.logger.info(MODULE_LOADING.format("Loading", module))
                    super().load_extension(MODULE_PATH.format(module))
                    self.logger.info(MODULE_LOADING.format("Loaded", module))
            else:
                if enabled:
                    self.logger.info(MODULE_LOADING.format("Loading", module))
                    super().load_extension(MODULE_PATH.format(module))
                    self.logger.info(MODULE_LOADING.format("Loaded", module))

            self.module_config.save()

    async def dispatch_server_command(self, server, command, *args):
        command = ServerCommand.get_from_name(command)
        command_ctx = ServerContext(server, self)
        await command.invoke(command_ctx, args)

    async def on_ready(self):
        self.logger.info(f"{self.user.name} is now online!")

    def __repr__(self):
        return f"LiteBot: Version: {LiteBot.VERSION}"
