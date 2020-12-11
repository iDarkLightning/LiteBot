import json, discord

class ConfigMap(dict):
    def __init__(self, value=None):
        super().__init__(self)

        if value:
            self.update(value)

    def get(self, key, default=None):
        # Allow . lookup when using `get`
        if '.' in key:
            key_items = key.split('.', 1)

            if len(key_items) == 2:
                sub_config = self.get(key_items[0], {})

                # Recurse to perform next lookup
                return sub_config.get(key_items[1], default)
        
        # Value lookup
        value = dict.get(self, key,  default)

        # Convert dictionaries back to ConfigMap's so you can use dotted access
        if isinstance(value, dict):
            return ConfigMap(value=value)

        return value

    def set(self, key, value):
        if isinstance(value, dict):
            value = ConfigMap(value=value)

        dict.__setattr__(self, key, value)

    def __getattr__(self, key):
        return self.get(key)

    def __setattr__(self, key, value):
        self.set(key, value)

    def get_colour(self, key, default=None):
        if key in self.get('colours', {}):
            return discord.Colour(self['colours'][key])

        if default:
            return default

        raise AttributeError(key)

    __getitem__ = __getattr__
    __setitem__ = __setattr__
    __delitem__ = dict.__delattr__
    
class BotConfig(ConfigMap):
    def __init__(self, config_location='config.json'):
        super().__init__(self)

        self._config_location = config_location

    def load_from_file(self):
        with open(self._config_location, 'r') as f:
            self.update(json.load(f))

        print(self)

    def save_to_file(self):
        with open(self._config_location, 'w') as f:
            json.dump(self, f)
            
def setup(bot):
    bot.config = BotConfig()
    bot.config.load_from_file()
