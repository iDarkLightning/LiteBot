import json
import os
import sys
from typing import Optional
from ..utils.logging import get_logger

CONFIG_DIR_NAME = "config"
logger = get_logger("bot")

class BaseConfig(dict):
    DEFAULT_CONFIG = {}

    def __init__(self, file_name: str, required: bool) -> None:
        super().__init__(self)
        self.file_path = os.path.join(os.getcwd(), CONFIG_DIR_NAME, file_name)
        self.required = required
        self._load_from_file()

    def _load_from_file(self) -> None:
        """
        Loads the config from `self.file_path`
        Writes DEFAULT_CONFIG if there is no valid config file at the path
        """
        try:
            with open(self.file_path) as f:
                self.update(json.load(f))
            self._match_default(self, self.file_path)
        except FileNotFoundError:
            logger.warning(f"No file found at {self.file_path}! Writing Default!")
            self._write_default_config(self.file_path)
            if self.required:
                logger.error("Required config file has been generated. Please fill it out and restart!")
                sys.exit()

    @classmethod
    def _write_default_config(cls, file_path: str) -> None:
        """
        Writes the default config as specified in the class
        :param file_path: The path to the file which will be written
        :type file_path: str
        """
        with open(file_path, "w") as f:
            json.dump(cls.DEFAULT_CONFIG, f, indent=4, separators=(",", ":"))

    @classmethod
    def _match_default(cls, instance, file_path) -> None:
        """
        Compares current config with default config, and
        adds all missing keys to the config
        :param instance: The instance config to match
        :type instance: CongigBase
        """
        if cls.DEFAULT_CONFIG.keys() == instance.keys():
            return

        for key in cls.DEFAULT_CONFIG:
            if key not in instance:
                instance[key] = cls.DEFAULT_CONFIG[key]

        instance.save()
        if instance.required:
            logger.error(f"There are new fields in required config at {file_path}. Please fill it out and restart")
            sys.exit()

    def save(self) -> None:
        """
        Saves the current config
        """
        with open(self.file_path, "w") as f:
            json.dump(self, f, indent=4, separators=(",", ":"))


class MainConfig(BaseConfig):
    # The bot's default config
    DEFAULT_CONFIG = {
        "token": "BOT TOKEN",
        "prefixes": [],
        "main_guild_id": 0,
        "members_role": [],
        "operators_role": [],
        "log_channel_id": 0,
        "api_secret": "API SECRET",
        "servers": {
            "name": {
                "numerical_server_ip": "THE SERVER IP ADDRESS, NO DNS",
                "server_port": 25565,
                "rcon_port": 25575,
                "rcon_password": "THE PASSWORD FOR RCON CONNECTION",
                "operator": True,
                "bridge_channel_id": 0
            }
        }
    }

    def __init__(self, file_name: str = "config.json") -> None:
        super().__init__(file_name, True)

class ModuleConfig(BaseConfig):
    def __init__(self, file_name: str = "modules_config.json") -> None:
        super().__init__(file_name, False)

    def register_cog(self, module: str, cog_name: str, val: Optional[bool] = False) -> None:
        """
        Toggles whether or not a cog is enabled,
        sets to false by default or if the cog has not been registered previously.
        :param module: The module the cog belongs to
        :type module: str
        :param cog_name: The name of the cog
        :type cog_name: str
        :param val: The value to set the cog's status to
        :type val: Optional[bool]
        """
        try:
            self[module]["cogs"][cog_name] = val
        except KeyError:
            self[module]["cogs"] = {}
            self[module]["cogs"][cog_name] = val

        self.save()

    def cog_enabled(self, module: str, cog_name: str) -> bool:
        """
        Checks whether a cog is enabled. Registers it as false
        if the cog has not been previously registered
        :param module: The module the cog belongs to
        :type module: str
        :param cog_name: The name of the cog
        :type cog_name: str
        :return: Whether or not the cog is enabled
        :rtype: bool
        :raises: ModuleNotFoundError
        """
        if self.get(module) is None:
            raise ModuleNotFoundError

        try:
            return self[module]["cogs"][cog_name]
        except KeyError:
            self.register_cog(module, cog_name)
            logger.warning(f"The cog: {cog_name} for module: {module} has been registered. It is disabled by default, you can enable it at {self.file_path}")
            return False

    def match_module(self, module: str, config: dict) -> None:
        """
        Matches the default config for a module with the current config
        :param module: The module to match
        :type module: str
        :param config: The config to match it to
        :type config: dict
        """
        if module not in self:
            self[module] = {"enabled": False, "config": config}
            logger.warning(f"Wrote default config for module: {module}. Please fill it out, and reload the module/restart the bot.")
            self.save()
            return

        if "config" not in self[module]:
            self[module]["config"] = {}

        for key in config:
            if not key in self[module]["config"]:
                self[module]["config"][key] = config[key]

    def register_module(self, module: str, initial_val: Optional[bool] = False) -> None:
        """
        Registers a new module
        :param module: The module to register
        :type module: str
        :param initial_val: The initial value to register the module as
        :type initial_val: Optional[bool]
        """
        self[module] = {"enabled": initial_val}
        logger.info(f"Registed a new module: {module}. It has been disabled by default, you can enable it at {self.file_path}")

    def toggle_module(self, module: str, val: bool) -> None:
        if self.get(module) is None:
            raise ModuleNotFoundError

        self[module]["enabled"] = val
        self.save()

    def toggle_cog(self, module: str, cog_name: str, val: bool) -> None:
        if self.get(module) is None:
            raise ModuleNotFoundError

        self[module]["cogs"][cog_name] = val
        self.save()