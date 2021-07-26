from __future__ import annotations

import inspect
from typing import Callable, TYPE_CHECKING
from enum import Enum

from litebot.utils.config import SettingsConfig

if TYPE_CHECKING:
    from litebot.core import Cog, LiteBot, Plugin

class SettingTypes(Enum):
    DISC_COMMAND = "DISC_COMMAND_SETTING"
    MC_COMMAND = "MC_COMMAND_SETTING"
    EVENT = "EVENT_SETTING"
    TASK = "TASK"
    MISC = "MISC_SETTING"

class Setting:
    def __init__(self, callback: Callable, **kwargs):
        self.cog = None
        self.plugin = None
        self.__callback = callback
        
        try:
            self.__name = kwargs["name"]
        except KeyError:
            raise KeyError("Setting must provide a name!")

        self.type = kwargs.get("type", SettingTypes.MISC)
        self.__description = kwargs.get("description", "This _setting does not have a description!")
        self.__config = kwargs.get("config", {})

        self.__enabled = False
        self.__id_checks = []
        self.__op_level = 0

    @property
    def enabled(self):
        """
        Returns:
            Whether or not the settings is enabled
        """
        return self.__enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.__enabled = value

    @property
    def id_checks(self):
        """
        Notes:
            Only available for disocrd command settings, else None

        Returns:
            The discord ID checks that the executor must meet in order to execute the setting.
        """
        return self.__id_checks

    @id_checks.setter
    def id_checks(self, value):
        self.__id_checks = value

    @property
    def op_level(self):
        """
        Notes:
            Only available for minecraft command settings, else None

        Returns:
            The required OP level to execute the command
        """
        return self.__op_level

    @op_level.setter
    def op_level(self, value: int):
        if value > 4:
            raise ValueError("OP Level cannot be greater than 4!")
        self.__op_level = value

    @property
    def callback(self):
        """
        Returns:
            The callback for the setting
        """
        return self.__callback

    @property
    def name(self):
        """
        Returns:
            The name of the setting
        """
        return self.__name

    @property
    def description(self):
        """
        Returns:
            The description of the setting
        """
        return self.__description

    @property
    def config(self):
        """
        Returns:
            The configuration for the setting
        """
        return self.__config

    @config.setter
    def config(self, value):
        self.__config = value

    def serialize(self):
        """
        Returns:
            A JSON-serialized version of the setting
        """
        serialized = {
            "enabled": False,
        }

        if self.__config:
            serialized["config"] = self.__config

        if self.type == SettingTypes.DISC_COMMAND:
            serialized["id_checks"] = []
        elif self.type == SettingTypes.MC_COMMAND:
            serialized["op_level"] = 0

        return serialized

class SettingsManager:
    def __init__(self):
        self.settings = {}
        self.__settings_file = SettingsConfig()

    @property
    def settings_file(self) -> SettingsConfig:
        """
        Returns:
            The settings config file
        """
        return self.__settings_file

    def update_setting(self, setting: Setting) -> None:
        """Update the settings file from the setting object

        Args:
            setting: The setting to update
        """
        file_vals = self.__settings_file[setting.plugin.meta.repr_name]["settings"][setting.name]
        file_vals["enabled"] = setting.enabled

        if "id_checks" in file_vals:
            file_vals["id_checks"] = setting.id_checks
        elif "op_level" in file_vals:
            file_vals["op_level"] = setting.op_level

        if setting.config:
            file_vals["config"] = setting.config

        self.__settings_file.save()

    def update_plugin(self, plugin: Plugin) -> None:
        """Update the settings file from the plugin object

        Args:
            plugin: The plugin to update
        """
        file_vals = self.__settings_file[plugin.meta.repr_name]
        file_vals["id_checks"] = plugin.id_checks
        file_vals["op_level"] = plugin.op_level

        file_vals["config"] = plugin.config

        for setting in self.settings.values():
            if setting.id_checks is not None:
                setting.id_checks = setting.id_checks or setting.plugin.id_checks

            if setting.op_level is not None:
                setting.op_level = setting.op_level or setting.plugin.op_level

        self.__settings_file.save()

    def add_settings(self, cog: Cog, bot: LiteBot, plugin: Plugin, settings: list[Setting]) -> None:
        """Load all the settings for a cog

        Args:
            cog: The cog to load all the settings for
            bot: The bot object
            plugin: The plugin the settings belong to
            settings: The settings to load
        """
        for setting in settings:
            self.settings[setting.name] = setting
            setting.cog = cog
            setting.plugin = plugin

            plugin_name = plugin.meta.repr_name

            if inspect.isfunction(setting.config):
                setting.config = setting.config(bot)

            if setting.name not in self.__settings_file[plugin_name]["settings"].keys():
                self.__settings_file[plugin_name]["settings"][setting.name] = setting.serialize()
            else:
                setting.enabled = self.__settings_file[plugin_name]["settings"][setting.name]["enabled"]

                if (checks := self.__settings_file[plugin_name]["settings"][setting.name].get("id_checks")) is not None:
                    setting.id_checks = checks or plugin.id_checks
                elif (level := self.__settings_file[plugin_name]["settings"][setting.name].get("op_level", 0)) is not None:
                    setting.op_level = level or plugin.op_level

                if not setting.config:
                    continue

                conf = self.__settings_file[plugin_name]["settings"][setting.name].get("config", {})
                if conf.keys() != setting.config.keys():
                    self.__settings_file[plugin_name]["settings"][setting.name]["config"] = conf | {k: v for k, v in setting.
                        config.items() if k not in conf.keys()}

                setting.config = self.__settings_file[plugin_name]["settings"][setting.name]["config"]

        self.__settings_file.save()

    def add_plugin(self, plugin: Plugin) -> None:
        """Load a plugin

        Args:
            plugin: The plugin to add
        """
        settings = self.__settings_file.get(plugin.meta.repr_name, {"settings": {}}).get("settings", {})

        self.__settings_file[plugin.meta.repr_name] = plugin.serialize() | {"settings": settings}
        self.__settings_file.save()