import json
import os
from typing import Any, Optional
from ..errors import ConfigFirstGenerated, NewConfigFields

CONFIG_DIR_NAME = "config"

class ConfigMap(dict):
    def __init__(self, value: Optional[dict] = None) -> None:
        super().__init__(self)

        if value:
            self.update(value)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Allows . lookup when using `get`

        Example
        --------
        .. code-block :: python3
            obj = ConfigMap({
                "primary": {
                    "secondary": {
                        "key": "value"
                    }
                }
            })

            value = obj.primary.seconday.key

        :param key: The path to the value to get
        :type key: str
        :param default: Default value to get
        :type default: any
        :return: The value at the specified key
        :rtype: any
        """
        if '.' in key:
            key_items = key.split('.', 1)

            if len(key_items) == 2:
                sub_config = self.get(key_items[0], {})

                # Recurse to perform next lookup
                return sub_config.get(key_items[1], default)

        # Value lookup
        value = dict.get(self, key, default)

        # Convert dictionaries back to ConfigMap's so you can use dotted access
        if isinstance(value, dict):
            return ConfigMap(value=value)

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Sets the value of an attribute
        :param key: The attribute to set
        :type key: str
        :param value: The value to set the attribute to
        :type value: any
        """
        if isinstance(value, dict):
            value = ConfigMap(value=value)
        dict.__setattr__(self, key, value)

    def __getattr__(self, key: str) -> Any:
        return self.get(key)

    def __setattr__(self, key: str, value: Any):
        self.set(key, value)

    # Sets __getitem__ & __setitem__ to work in same fashion as __getattr & __setattr__
    __getitem__ = __getattr__
    __delitem__ = dict.__delattr__


class BaseConfig(ConfigMap):
    DEFAULT_CONFIG = {}

    def __init__(self, file_name: str) -> None:
        super().__init__(self)
        self._file_path = os.path.join(os.getcwd(), CONFIG_DIR_NAME, file_name)
        self._load_from_file()

    def _load_from_file(self) -> None:
        """
        Loads the config from `self._file_path`
        Writes DEFAULT_CONFIG if there is no valid config file at the path
        """
        try:
            with open(self._file_path) as f:
                self.update(json.load(f))
            self._match_default(self, self._file_path)
        except FileNotFoundError:
            print(f"No file found at {self._file_path}! Writing Default!")
            self._write_default_config(self._file_path)
            raise ConfigFirstGenerated(f"Generated file at {self._file_path}. Please fill it out and restart!")

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
        :param instance:
        :type instance:
        """
        if cls.DEFAULT_CONFIG.keys() == instance.keys():
            return

        for key in cls.DEFAULT_CONFIG:
            if key not in instance:
                instance[key] = cls.DEFAULT_CONFIG[key]

        instance.save()
        raise NewConfigFields(
            f"New fields have been added to the config at {file_path}. Please fill it out and restart!")

    def save(self) -> None:
        """
        Saves the current config
        """
        with open(self._file_path, "w") as f:
            json.dump(self, f, indent=4, separators=(",", ":"))


class MainConfig(BaseConfig):
    # The bot's default config
    DEFAULT_CONFIG = {
        "token": "",
        "prefixes": [],
        "server_logo": "",
        "main_guild_id": 1,
        "members_role": [],
        "operators_role": [],
        "servers": {
            "name": {
                "server_ip": "",
                "server_port": 25565,
                "rcon_port": 25575,
                "rcon_password": "",
                "operator": True,
                "bridge_channel_id": 1
            }
        }
    }

    def __init__(self, file_name: str = "config.json") -> None:
        super().__init__(file_name)


class ModuleConfig(BaseConfig):
    def __init__(self, file_name: str = "modules_config.json") -> None:
        super().__init__(file_name)

    def _load_from_file(self) -> None:
        try:
            super()._load_from_file()
        except ConfigFirstGenerated:
            print("Blank modules_config has been generated!")
