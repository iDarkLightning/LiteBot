from __future__ import annotations

import importlib
import os
import re
from typing import TYPE_CHECKING, Optional

from litebot.core import Cog

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
            "description": self.description,
            "id_checks": [],
            "op_level": 0
        }


class Plugin:
    def __init__(self, path, module):
        self.config: dict = {}
        self.cogs: list[Cog] = []
        self.id_checks = []
        self.op_level = 0
        self.module = module
        self.path = path
        self.meta = _PluginMeta(self.path, **getattr(self.module, "__plugin_meta__"))
        self.authors = self.meta.authors
        self.description = self.meta.description

    def serialize(self):
        return {
            "name": self.meta.name,
            "id": self.meta.id,
            "authors": self.authors,
            "description": self.description,
            "id_checks": self.id_checks,
            "op_level": self.op_level,
            "config": self.config
        }

class PluginManager:
    def __init__(self, bot: LiteBot):
        self._bot = bot
        self.all_plugins = self._init_plugins()

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
                    plugin = Plugin(f"plugins.{path}", module)

                    if plugin.meta.repr_name not in self._bot.settings_manager.settings_file:
                        self._bot.settings_manager.settings_file[plugin.meta.repr_name] = plugin.serialize()

                    if hasattr(module, "config"):
                        conf = self._bot.settings_manager.settings_file[plugin.meta.repr_name].get("config", {})
                        if conf.keys() != (config := getattr(module, "config")(self._bot)):
                            self._bot.settings_manager.settings_file[plugin.meta.repr_name]["config"] = conf | {k: v for k, v in config.items() if k not in conf.keys()}

                        plugin.config = self._bot.settings_manager.settings_file[plugin.meta.repr_name]["config"]

                    plugin.id_checks = self._bot.settings_manager.settings_file[plugin.meta.repr_name].get("id_checks", [])
                    plugin.op_level = self._bot.settings_manager.settings_file[plugin.meta.repr_name].get("op_level", 0)

                    self._bot.settings_manager.settings_file.save()
                    plugins[plugin.meta.id] = plugin

        return plugins

    def load_plugins(self):
        for plugin in self.all_plugins.values():
            self._bot.settings_manager.add_plugin(plugin)

            if hasattr(plugin.module, "requirements"):
                reqs = getattr(plugin.module, "requirements")
                if reqs(self):
                    self._bot.load_plugin(plugin)
            else:
                self._bot.load_plugin(plugin)

    def __getitem__(self, item):
        try:
            return self.all_plugins[item]
        except KeyError:
            for key in self.all_plugins.keys():
                if key.endswith(item):
                    return self.all_plugins[key]
