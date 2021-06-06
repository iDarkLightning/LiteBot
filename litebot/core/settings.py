from __future__ import annotations
from typing import Callable
from enum import Enum

from discord.ext.commands._types import _BaseCommand

from litebot.utils.config import SettingsConfig

class SettingTypes(Enum):
    COMMAND = "COMMAND_SETTING",
    EVENT = "EVENT_SETTING",
    MISC = "MISC_SETTING"

class Setting:
    def __init__(self, callback: Callable, **kwargs):
        self.plugin = None
        self.__callback = callback
        
        try:
            self.__name = kwargs["name"]
        except KeyError:
            raise KeyError("Setting must provide a name!")

        self._type = kwargs.get("type", SettingTypes.COMMAND)
        self.__description = kwargs.get("description", "This setting does not have a description!")
        self.__config = kwargs.get("config", {})

    @property
    def callback(self):
        return self.__callback

    @property
    def name(self):
        return self.__name

    @property
    def description(self):
        return self.__description

    @property
    def config(self):
        return self.__config

    @config.setter
    def config(self, value):
        self.__config = value

    def serialize(self):
        serialized = {
            "enabled": False,
        }

        if self.__config:
            serialized["config"] = self.__config

        if self._type == SettingTypes.COMMAND:
            serialized["id_checks"] = []

        return serialized

class SettingsManager:
    def __init__(self):
        self.__settings_file = SettingsConfig()
        self._settings = {}

    def setting_enabled(self, name):
        setting_: Setting = self._settings[name]
        return self.__settings_file[setting_.plugin]["settings"][setting_.name]["enabled"]

    def setting_enabled_(self, setting_: Setting):
        return self.__settings_file[setting_.plugin]["settings"][setting_.name]["enabled"]

    def disabled_settings(self):
        return [s for s in list(set(self._settings.values())) if not self.setting_enabled(s.name)]

    def add_settings(self, plugin_name: str, settings: list[Setting]):
        for setting in settings:
            self._settings[setting.name] = setting
            setting.plugin = plugin_name

            if setting.name not in self.__settings_file[plugin_name]["settings"].keys():
                self.__settings_file[plugin_name]["settings"][setting.name] = setting.serialize()
            else:
                if not setting.config:
                    continue

                conf = self.__settings_file[plugin_name]["settings"][setting.name]["config"]
                if conf.keys() != setting.config.keys():
                    self.__settings_file[plugin_name]["settings"][setting.name] = conf | {k: v for k, v in setting.
                        config.keys() if k not in conf.keys()}

                setting.config = self.__settings_file[plugin_name]["settings"][setting.name]["config"]

        self.__settings_file.save()

    def add_plugin(self, data):
        settings = self.__settings_file.get(data["id"], {"settings": {}}).get("settings", {})

        self.__settings_file[data["id"]] = data | {"settings": settings}
        self.__settings_file.save()
#
# def setting(**kwargs):
#     def decorator(func):
#         setting_ = Setting(func, **kwargs)
#         if isinstance(func, _BaseCommand):
#             func.callback.__setting__ = setting_
#             return func
#         func.__setting__ = setting_
#         return func
#     return decorator
