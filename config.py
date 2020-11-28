import json


class BotConfig:
    def __init__(self, path='config.json'):
        self._config = {}
        self.file_path = path

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __getitem__(self, item):
        return self.get(item)

    def get(self, key):
        return self._config[key]

    def set(self, key, value):
        self._config[key] = value

    def load(self):
        with open(self.file_path, 'r') as config:
            self._config = json.loads(config.read())

    def save(self):
        with open(self.file_path, 'w') as config:
            config.write(json.dumps(self._config, indent=4, separators=(',', ':')))

    # Enables an extension and writes config
    def add_module_config(self, name, module_config):
        if name == 'main':
            return

        if self.config_exists(name):
            self._config['modules'][name]['enabled'] = True
            self.save()
            return

        try:
            self._config['modules'][name]['config'] = module_config
            self._config['modules'][name]['enabled'] = True
        except KeyError:
            self._config['modules'] = {}
            self._config['modules'][name] = {}
            self._config['modules'][name]['config'] = module_config
            self._config['modules'][name]['enabled'] = True
        self.save()

    # Disables an extension
    def disable_config(self, name):
        if name == 'main':
            return

        try:
            self._config['modules'][name]['enabled'] = False
        except KeyError:
            self._config['modules'] = {}
            self._config['modules'][name] = {}
            self._config['modules'][name]['enabled'] = False
        self.save()

    # Set's a Cog's value to True
    def enable_cog(self, module, cog):
        self._config['modules'][f'modules.{module}']['cogs'] = {}
        self._config['modules'][f'modules.{module}']['cogs'][cog] = True
        self.save()

    # Sets a Cog's Value to False
    def disable_cog(self, module, cog):
        self._config['modules'][f'modules.{module}']['cogs'][cog] = False
        self.save()

    # Loads the servers info
    def set_servers(self):
        servers = {}
        for server in self._config['servers']:
            servers[server] = self._config['servers'][server]
        return servers

    # Checks if there is a config available for the module
    def config_exists(self, name):
        try:
            config_exists = self._config['modules'][name]
            if len(config_exists) > 2:
                return True
            else:
                return False
        except KeyError:
            return False
