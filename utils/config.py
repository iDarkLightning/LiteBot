import json
import os
import importlib

class BotConfig:
    def __init__(self, main_path='config.json', module_path='modules_config.json'):
        self._config = {}
        self._module_config = {}
        self.file_path = main_path
        self.module_path = module_path
        self.load()
        self.load_module_config()
        self.init_module_config()

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

    def load_module_config(self):
        try:
            with open(self.module_path, 'r') as module_config:
                module_config = json.loads(module_config.read())
                self._config['modules'] = module_config
        except FileNotFoundError:
            with open(self.module_path, 'w') as module_config:
                json.dump({}, module_config)
    
    def save_module_config(self):
        with open(self.module_path, 'w') as module_config:
            module_config.write(json.dumps(self._config['modules'], indent=4, separators=(',', ':')))
            

    # Enables an extension and writes config
    def init_module_config(self):
        modules = list(
            filter(lambda path: os.path.isdir(f'./modules/{path}') and path != '__pycache__', os.listdir('./modules')))
        module_config = self._config['modules']
        for module in modules:
            if self.module_exists(module):
                if module_config[module]['enabled'] is not True:
                    module_config[module]['enabled'] = False

                config_func = self.get_config(module)
                config = config_func()

                if config:
                    if self.module_config(module) is not False:
                        if config.keys() != self.module_config(module).keys():
                            module_config[module]['config'] = config
                    else:
                        module_config[module]['config'] = config
                else:
                    if self.module_config(module) is not False:
                        del module_config[module]['config']
            else:
                config_func = self.get_config(module)
                config = config_func()
                module_config[module] = {}
                module_config[module]['enabled'] = False
                if config:
                    module_config[module]['config'] = config
        self.save_module_config()


    def get_config(self, module):
        spec = importlib.util.find_spec(f'modules.{module}')
        lib = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(lib)
        except Exception as e:
            raise Exception

        try:
            config = getattr(lib, 'config')
            return config
        except AttributeError as e:
            raise AttributeError

    #Enables an extension
    def enable_config(self, name):
        if name == 'main':
            return

        config = self._config['modules']

        try:
            config[name]['enabled'] = True
        except KeyError as error:
            print(error)
        self.save_module_config()

    # Disables an extension
    def disable_config(self, name):
        if name == 'main':
            return

        config = self._config['modules']

        try:
            config[name]['enabled'] = False
        except KeyError as error:
            print(error)
        self.save_module_config()

    # Set's a Cog's value to True
    def enable_cog(self, module, cog):
        config = self._config['modules']

        try:
            config[module]['cogs'][cog] = True
        except KeyError:
            config[module]['cogs'] = {}
            config[module]['cogs'][cog] = True
        self.save_module_config()

    # Sets a Cog's Value to False
    def disable_cog(self, module, cog):
        self._config['modules'][module]['cogs'][cog] = False
        self.save()

    # Loads the servers info
    def set_servers(self):
        servers = {}
        for server in self._config['servers']:
            servers[server] = self._config['servers'][server]
        return servers

    # Checks if there is a module already
    def module_exists(self, name):
        try:
            module_exists = self._config['modules'][name]
            return True
        except KeyError:
            return False

    def module_config(self, name):
        try:
            module_config = self._config['modules'][name]['config']
            return module_config
        except KeyError:
            return False