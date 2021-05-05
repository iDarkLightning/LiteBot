from __future__ import annotations

import importlib.util
from typing import Union, Optional, Callable

from discord.ext.commands import errors

from litebot.core import Cog
from litebot.errors import ModuleLoadError, UnsatisfiedRequirements
from litebot.litebot import LiteBot
from litebot.utils.config import ModuleConfig
from litebot.utils.data_manip import snakify


def _module_method(func):
    func.__module_method__ = True
    return func

class Module:
    def __init__(self, **kwargs):
        try:
            self.name = kwargs["name"]
        except KeyError:
            raise KeyError("You must provide a name for your module!")

        self.id = snakify(self.name)
        self.version = kwargs.get("version", "1.0.0")
        self.description = kwargs.get("description")
        self.author = kwargs.get("author", "iDarkLightning")
        self.dependencies = kwargs.get("requires")

        self.bot: Optional[LiteBot] = None # Set during load

        self._cogs = {}
        self.__setup__: Optional[Callable] = None
        self.__requirements__: Optional[Callable] = None
        self.__config__: Optional[Callable] = None

    @property
    def config(self):
        return self.bot.module_config[self.id]["config"]

    @property
    def _cog_data(self):
        return self.bot.module_config[self.id]["cogs"]

    def set_setup(self, func):
        self.__setup__ = func
        return func

    def set_requirements(self, func):
        self.__requirements__ = func
        return func

    def set_config(self, func):
        self.__config__ = func
        return func

    def add_cog(self, cog: type, required: bool = False, *args) -> None:
        if not issubclass(cog, Cog):
            raise ModuleLoadError("Cog must be a subclass of litebot.core.Cog")

        if required:
            self._cogs[cog.__cog_name__] = (cog, args)
            return

        if cog.__cog_name__ not in self._cog_data:
            self.bot.module_config.register_cog(self.id, cog.__cog_name__)

        if self.bot.module_config.cog_enabled(self.id, cog.__cog_name__):
            self.bot.logger.info(f"Loaded cog: {cog.__cog_name__}")
            self._cogs[cog.__cog_name__] = (cog, args)

    def _inject(self, bot: LiteBot):
        self.bot = bot

        if not self.__setup__:
              raise errors.NoEntryPointError(f"Module {self.name} has no setup function!")

        self.__setup__(bot)

        uninstalled_deps = [dep for dep in self.dependencies if not importlib.util.find_spec(dep)]
        if uninstalled_deps:
            raise UnsatisfiedRequirements(
                f"Module: {self.name} could not be loaded because the following required dependencies are not loaded: {', '.join(self.dependencies)}")

        for cog_name, cog in self._cogs:
            instance: Cog = cog[0](self, bot, *cog[1])
            # self.bot.add_cog(instance)

    @_module_method
    def on_module_load(self):
        pass

    @_module_method
    def on_module_unload(self):
        pass

    @_module_method
    async def on_module_command(self, ctx):
        pass


    def __repr__(self):
        return f"<name={self.name} author={self.author} description={self.description}>"