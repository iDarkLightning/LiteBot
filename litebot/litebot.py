import importlib
import discord
import os
import mongoengine
from discord.ext import commands

from .core import Cog
from .minecraft.commands.action import ServerCommand, ServerEvent
from .utils.config import MainConfig, ModuleConfig
from .utils.logging import get_logger
from .minecraft.server import MinecraftServer, ServerContainer
from .utils.fmt_strings import MODULE_LOADING, MODULE_PATH
from litebot.modules.system.help_command import HelpCommand
from .utils.misc import Toggleable

MODULES_PATH = "litebot/modules"
REQUIRED_MODULES = (
    "litebot.modules.system",
    "litebot.modules.core"
)

class LiteBot(commands.Bot):
    VERSION = 3.0

    def __init__(self):
        self.config = MainConfig()
        self.module_config = ModuleConfig()
        self.server_commands = {}
        self.server_events = {k: [] for k in ServerEvent.VALID_EVENTS}

        super().__init__(
            command_prefix=commands.when_mentioned_or(*self.config["prefixes"]),
            help_command=HelpCommand(),
            intents=discord.Intents.all(),
            case_insensitive=True)
        self.logger = get_logger("bot")

        self.db = mongoengine.connect("bot", host="mongo", port=27017)
        self.logger.info("Connected to Mongo Database")

        self._cur_module = None
        self._initialising = Toggleable()
        self.servers = ServerContainer()

        self.using_lta = bool(os.environ.get("USING_LTA"))
        self._init_servers()

    def _init_servers(self):
        for server in self.config["servers"]:
            self.servers.append(MinecraftServer(server, self, **self.config["servers"][server]))

    @property
    def log_channel(self) -> discord.TextChannel:
        return self.get_channel(self.config["log_channel_id"])

    async def guild(self) -> discord.Guild:
        await self.wait_until_ready()
        return self.get_guild(self.config["main_guild_id"])

    def add_cog(self, cog: Cog, required: bool = False) -> None:
        if self._initialising and not required:
            self.module_config.register_cog(self._cur_module, cog.__cog_name__)

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
                                      and path != "__pycache__" and MODULE_PATH.format(path) not in REQUIRED_MODULES,
                         os.listdir(os.path.join(os.getcwd(), MODULES_PATH)))

        for module in modules:
            spec = importlib.util.find_spec(MODULE_PATH.format(module))
            lib = importlib.util.module_from_spec(spec)

            try:
                spec.loader.exec_module(lib)
            except Exception as e:
                self.logger.exception(e, exc_info=e)

            if hasattr(lib, "config"):
                config = getattr(lib, "config")(self)
                self.module_config.match_module(module, config)
            else:
                if module not in self.module_config:
                    self.module_config.register_module(module)

            self._cur_module = module
            enabled = self.module_config[module]["enabled"]
            if not enabled and not self.module_config[module].get("cogs"):
                with self._initialising:
                    super().load_extension(MODULE_PATH.format(module))
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

    def load_extension(self, name, *, package=None):
        if "." not in name:
            self._cur_module = name
        else:
            self._cur_module = name.split(".")[-1]

        super().load_extension(name)

    def add_command(self, command):
        if not isinstance(command, ServerCommand):
            return super().add_command(command)

        self.server_commands[command.full_name] = command

    def remove_command(self, name):
        if name not in self.server_commands:
            return super().remove_command(name)

        self.server_commands.pop(name)

    def add_event(self, event):
        self.server_events[event.name].append(event)

    def remove_event(self, name, cog):
        self.server_events[name] = list(filter(lambda e: e.cog is not cog, self.server_events[name]))

    async def on_ready(self):
        self.logger.info(f"{self.user.name} is now online!")

    def __repr__(self):
        return f"LiteBot: Version: {LiteBot.VERSION}"
