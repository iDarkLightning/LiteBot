from __future__ import annotations
from typing import Callable
from enum import Enum

from discord.ext.commands._types import _BaseCommand

from litebot.utils.config import SettingsConfig

class SettingTypes(Enum):
    DISC_COMMAND = "DISC_COMMAND_SETTING"
    MC_COMMAND = "MC_COMMAND_SETTING"
    EVENT = "EVENT_SETTING"
    MISC = "MISC_SETTING"

class Setting:
    def __init__(self, callback: Callable, **kwargs):
        self.plugin = None
        self.__callback = callback
        
        try:
            self.__name = kwargs["name"]
        except KeyError:
            raise KeyError("Setting must provide a name!")

        self._type = kwargs.get("type", SettingTypes.MISC)
        self.__description = kwargs.get("description", "This setting does not have a description!")
        self.__config = kwargs.get("config", {})
        self.__enabled = False
        self.__id_checks = []
        self.__op_level = 0

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.__enabled = value

    @property
    def id_checks(self):
        if self._type != SettingTypes.DISC_COMMAND:
            raise TypeError("ID Checks are only available for discord commands!")
        return self.__id_checks

    @id_checks.setter
    def id_checks(self, value):
        self.__id_checks = value

    @property
    def op_level(self):
        if self._type != SettingTypes.MC_COMMAND:
            raise TypeError("OP Level is only available for minecraft commands!")
        return self.__op_level

    @op_level.setter
    def op_level(self, value: int):
        if value > 4:
            raise ValueError("OP Level cannot be greater than 4!")
        self.__op_level = value

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

        if self._type == SettingTypes.DISC_COMMAND:
            serialized["id_checks"] = []
        elif self._type == SettingTypes.MC_COMMAND:
            serialized["op_level"] = 0

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

            setting.enabled = self.__settings_file[plugin_name]["settings"][setting.name]["enabled"]

            if checks := self.__settings_file[plugin_name]["settings"][setting.name].get("id_checks"):
                setting.id_checks = checks
            elif level := self.__settings_file[plugin_name]["settings"][setting.name].get("op_level"):
                setting.op_level = level

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