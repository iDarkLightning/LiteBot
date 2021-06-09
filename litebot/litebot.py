import asyncio
import importlib
from typing import Callable, Union

import discord
import os
import mongoengine
from discord.ext import commands
from discord.ext.commands import Command

from litebot.core import context
from litebot.core.minecraft.commands.action import ServerCommand, ServerEvent
from .core.plugins import PluginManager
from .core.settings import SettingsManager
from .utils.config import MainConfig, ModuleConfig
from .utils.logging import get_logger
from litebot.core.minecraft.server import MinecraftServer, ServerContainer
from .utils.fmt_strings import MODULE_LOADING, MODULE_PATH
from litebot.modules.system.help_command import HelpCommand
from .utils.misc import Toggleable

MODULES_PATH = "litebot/test_modules"
REQUIRED_MODULES = (
    # "litebot.modules.system",
    # "litebot.modules.core"
)

class LiteBot(commands.Bot):
    VERSION = 3.0

    def __init__(self):
        self.config = MainConfig()
        self.module_config = ModuleConfig()
        self.plugin_manager = PluginManager(self)
        self.settings_manager = SettingsManager()
        self.server_commands: dict[str, ServerCommand] = {}
        self.server_events: dict[str, list[Callable]] = {k: [] for k in ServerEvent.VALID_EVENTS}

        super().__init__(
            command_prefix=commands.when_mentioned_or(*self.config["prefixes"]),
            help_command=HelpCommand(),
            intents=discord.Intents.all(),
            case_insensitive=True)
        self.logger = get_logger("bot")

        self.db = mongoengine.connect("bot", host="mongo", port=27017)
        self.logger.info("Connected to Mongo Database")

        self.processing_plugin = None
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

    async def get_context(self, message, *, cls=context.Context):
        return await super().get_context(message, cls=cls)

    def _schedule_event(self, coro, event_name, *args, **kwargs):
        if hasattr(coro, "__setting__"):
            args = (coro.__setting__, *args)
        wrapped = self._run_event(coro, event_name, *args, **kwargs)
        return asyncio.create_task(wrapped, name=f"discord.py: {event_name}")

    def load_plugin(self, plugin):
        self.processing_plugin = plugin
        super().load_extension(plugin.path)

    def unload_plugin(self, plugin):
        self.processing_plugin = plugin
        super().unload_extension(plugin.path)

    def add_command(self, command: Union[ServerCommand, Command]):
        if not isinstance(command, ServerCommand):
            return super().add_command(command)

        self.server_commands[command.full_name] = command

    def remove_command(self, name):
        if name not in self.server_commands:
            return super().remove_command(name)

        self.server_commands.pop(name)

    def add_server_listener(self, event, name):
        self.server_events[name].append(event)

    def remove_server_listener(self, func, name):
        self.server_events[name] = list(filter(lambda e: e is not func, self.server_events[name]))

    async def on_ready(self):
        self.logger.info(f"{self.user.name} is now online!")

    def __repr__(self):
        return f"LiteBot: Version: {LiteBot.VERSION}"
