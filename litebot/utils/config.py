import json
import os
import sys
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

class SettingsConfig(BaseConfig):
    def __init__(self, file_name: str = "settings.json") -> None:
        super().__init__(file_name, False)