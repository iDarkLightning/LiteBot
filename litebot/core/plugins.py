from __future__ import annotations

import os
from typing import TYPE_CHECKING
import re
import importlib

from sanic import Blueprint

if TYPE_CHECKING:
    from litebot.litebot import LiteBot

class _PluginMeta:
    def __init__(self, id_: str, **kwargs):
        self.name = kwargs.get("name", id_.rsplit(".", 1)[-1])
        self.id = id_
        self.repr_name = self.id.rsplit(".", 1)[-1]
        self.authors = kwargs.get("authors", [])
        self.description = kwargs.get("description", "This plugin does not have a description!")

    def serialize(self):
        return {
            "name": self.name,
            "id": self.id,
            "authors": self.authors,
            "description": self.description
        }

class Plugin:
    def __init__(self, path, module):
        self.module = module
        self.path = path
        self.meta = _PluginMeta(self.path, **getattr(self.module, "__plugin_meta__"))
        self.authors = self.meta.authors
        self.description = self.meta.description
        self.blueprint_group: Blueprint.group = Blueprint.group(url_prefix=f"/{self.meta.repr_name}")

class PluginManager:
    def __init__(self, bot: LiteBot):
        self._bot = bot
        self._all_plugins = self._init_plugins()

    def _init_plugins(self):
        plugins = {}
        for root, dirs, files in os.walk(os.path.join(os.getcwd(), "plugins")):
            for plugin_name in [*dirs, *files]:
                path = os.path.join(root, plugin_name).split("/plugins/", 2)[1].replace("/", ".").removesuffix(".py")

                if re.match(".*__.*__", path):
                    continue


                try:
                    module = importlib.import_module(f"plugins.{path}")
                except ModuleNotFoundError:
                    continue

                if hasattr(module, "__plugin_meta__") and hasattr(module, "setup"):
                    plugin = Plugin(f"plugins.{path}",module)
                    plugins[plugin.meta.id] = plugin

        return plugins

    def load_plugins(self):
        for plugin in self._all_plugins.values():
            self._bot.settings_manager.add_plugin(plugin.meta)

            if hasattr(plugin.module, "requirements"):
                reqs = getattr(plugin.module, "requirements")
                if reqs(self):
                    self._bot.load_plugin(plugin)
            else:
                self._bot.load_plugin(plugin)

    def __getitem__(self, item):
        try:
            return self._all_plugins[item]
        except KeyError:
            for key in self._all_plugins.keys():
                if key.endswith(item):
                    return self._all_plugins[key]
