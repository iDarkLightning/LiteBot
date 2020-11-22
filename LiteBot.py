import importlib
import sys
import discord
from discord.ext import commands
import datetime
from datetime import datetime
import json
from rcon import MCRcon
from config import BotConfig
import sqlite3
import os


class LiteBot(commands.Bot):
    def __init__(self):
        self.config = BotConfig()
        self.config.load()
        self.token = self.config['token']
        self.__extensions = {}
        super(LiteBot, self).__init__(command_prefix=self.config['prefix'], intents=discord.Intents.all())
        self.help_command = None
        self.servers = self.config.set_servers()
        self.rcons = self.init_rcons()
        self.database = sqlite3.connect('litebot.db')
        self.load_module('main')
        self.init_modules()
        self.system_commands()

    # Loads all available modules if they are enabled in config, else sets config to false
    def init_modules(self):
        modules = list(
            filter(lambda path: os.path.isdir(f'./modules/{path}') and path != '__pycache__', os.listdir('./modules')))
        for module in modules:
            try:
                if self.config['modules'][f'modules.{module}']['enabled']:
                    self.load_module(f'modules.{module}')
            except KeyError:
                self.config.disable_config(f'modules.{module}')

    # Initalizes rcon objects for all servers in config and gets bridge channel if using LTA
    def init_rcons(self):
        rcons = {}
        for server in self.config['servers']:
            rcons[server] = {}
            rcon = MCRcon(
                self.config['servers'][server]['server_ip_numerical'],
                self.config['servers'][server]['server_rcon_password'],
                self.config['servers'][server]['server_rcon_port']
            )
            rcons[server]['rcon'] = rcon
            rcons[server]['bridge'] = rcon.get_bridge()[1]
        return rcons

    # Initializes system commands for help and module loading
    def system_commands(self):
        @self.command(brief='`help` displays this panel')
        async def help(ctx):
            embed = discord.Embed(title='LiteBot Help Panel', color=0xADD8E6, timestamp=datetime.utcnow())
            for command in self.commands:
                try:
                    command.checks[0](ctx)
                    embed.add_field(name=f'{str(command).capitalize()} Command', value=f'{command.brief}', inline=False)
                except IndexError:
                    embed.add_field(name=f'{str(command).capitalize()} Command', value=f'{command.brief}', inline=False)
                else:
                    pass
            await ctx.send(embed=embed)

        @self.command(brief='`module load|unload <module_name>`')
        @commands.has_permissions(administrator=True)
        async def module(ctx, action, module_name):
            try:
                if action.lower() == 'load':
                    self.load_module(f'modules.{module_name}')
                elif action.lower() == 'unload':
                    self.unload_module(f'modules.{module_name}')
            except commands.errors.ExtensionError as e:
                print(e)
                await ctx.send(f'An error occuring {action.lower()}ing that module')

    # Loads a module and writes config
    def load_module(self, name):
        if name in self.__extensions:
            raise commands.errors.ExtensionAlreadyLoaded(name)

        spec = importlib.util.find_spec(name)
        if spec is None:
            raise commands.errors.ExtensionNotFound(name)

        lib = importlib.util.module_from_spec(spec)
        sys.modules[name] = lib
        try:
            spec.loader.exec_module(lib)
        except Exception as e:
            del sys.modules[name]
            raise commands.errors.ExtensionFailed(name, e) from e

        try:
            setup = getattr(lib, 'setup')
        except AttributeError:
            del sys.modules[name]
            raise commands.errors.NoEntryPointError(name)

        try:
            config = setup(self)
            if config is not None:
                self.config.add_module_config(name, config)
        except Exception as e:
            del sys.modules[name]
            self._remove_module_references(lib.__name__)
            self._call_module_finalizers(lib, name)
            raise commands.errors.ExtensionFailed(name, e) from e
        else:
            self.__extensions[name] = lib

    # Unloads module and disables config
    def unload_module(self, name):
        if name == 'main':
            print('The main extension cannot be unloaded')
            return

        lib = self.__extensions.get(name)
        if lib is None:
            raise commands.errors.ExtensionNotLoaded(name)

        self._remove_module_references(lib.__name__)
        self._call_module_finalizers(lib, name)
        self.__extensions.pop(name, None)
        self.config.disable_config(name)

    # Loads a cog if is enabled in config
    def load_cog(self, module, cog):
        if module == 'main':
            super().add_cog(cog)
            return
        try:
            if self.config['modules'][f'modules.{module}']['cogs'][cog.__cog_name__]:
                print('ge')
                super().add_cog(cog)
        except KeyError:
            self.config.enable_cog(module, cog.__cog_name__)
            super().add_cog(cog)
