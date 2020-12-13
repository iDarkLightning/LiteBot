import importlib
import inspect
import discord
from discord.ext import commands
import datetime
from datetime import datetime
from utils.config import BotConfig
from utils import console
import sqlite3
import os, sys, traceback


class LiteBot(commands.Bot):
    def __init__(self):
        self.config = BotConfig()
        super().__init__(command_prefix=self.config['prefix'], intents=discord.Intents.all(),
                                      help_command=None)
        self.token = self.config['token']
        self.module_config = self.config['modules']
        self.servers = self.config.set_servers()
        self.rcons = self.init_rcons()
        self.flags = sys.argv
        self.db = sqlite3.connect('litebot.db')
        self.guild_id = self.config['main_guild_id']

    # Loads all available modules if they are enabled in config, else sets config to false
    def init_modules(self):
        super().load_extension('main')
        modules = list(
            filter(lambda path: os.path.isdir(f'./modules/{path}') and path != '__pycache__', os.listdir('./modules')))

        for module in modules:
            spec = importlib.util.find_spec(f"modules.{module}")
            lib = importlib.util.module_from_spec(spec)

            try:
                spec.loader.exec_module(lib)
            except Exception as e:
                print(e)

            if hasattr(lib, "config"):
                config = getattr(lib, "config")
                if "enabled" not in config or config["enabled"] is not True:
                    config["enabled"] = False

                for key in config:
                    if module in self.module_config:
                        if not key in self.module_config[module]:
                            self.module_config[module][key] = config[key]
                    else:
                        self.module_config[module] = config
            else:
                if module not in self.module_config or self.module_config[module]["enabled"] is not True:
                    self.module_config[module] = {"enabled": False}

            enabled = self.module_config[module]["enabled"]
            if hasattr(lib, "requirements"):
                requirements = getattr(lib, "requirements")
                if requirements(self) and enabled:
                    super().load_extension(f"modules.{module}")
                    console.log(f"Loaded {module}")
            else:
                if enabled:
                    super().load_extension(f"modules.{module}")
                    console.log(f"Loaded {module}")

        self.config.save_module_config()

    # Initalizes rcon objects for all servers in config and gets bridge channel if using LTA
    def init_rcons(self):
        rcons = {}
        for server in self.config['servers']:
            rcons[server] = {}
            rcon_details = [
                self.servers[server]['server_ip_numerical'],
                self.servers[server]['server_rcon_password'],
                self.servers[server]['server_rcon_port']
            ]
            rcons[server]['rcon'] = rcon_details
            bridge_channel_id = self.servers[server]['bridge_channel_id']
            if bridge_channel_id != 1:
                rcons[server]['bridge_channel'] = bridge_channel_id
            else:
                rcons[server][bridge_channel_id] = None
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
                except commands.CheckFailure:
                    pass
            await ctx.send(embed=embed)

        @self.command(brief='`module load|unload <module_name>`')
        @commands.has_permissions(administrator=True)
        async def module(ctx, action, module_name):
            try:
                if action.lower() == 'load':
                    self.load_extension(f'modules.{module_name}')
                    self.config.enable_config(module_name)
                elif action.lower() == 'unload':
                    self.unload_extension(f'modules.{module_name}')
                    self.config.disable_config(module_name)
            except commands.errors.ExtensionError as e:
                await ctx.send(f'An error occuring {action.lower()}ing that module')

    def error_handler(self):
        @self.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                return

            await generic_error_handler(ctx, error)

        async def generic_error_handler(ctx, error):
            if "-dev" in self.flags:
                stack_trace = "".join(traceback.format_exception(
                    type(error),
                    error,
                    error.__traceback__))

                await ctx.send(embed=discord.Embed(
                    title="Uh oh!",
                    description=f"An unknown exception occured\n```\n{stack_trace}\n```",
                    color=15158332))

            else:
                embed = discord.Embed(title="Uh oh!", color=15158332)

                if isinstance(error, commands.CommandInvokeError):
                    embed.description = "This command was used improperly, please refer to the help panel"

                if isinstance(error, commands.CheckFailure):
                    embed.description = "You do not have permission to use this command, contact an admin if you think this is a mistake"

                await ctx.send(embed=embed)

    # Loads a cog if is enabled in config
    def add_cog(self, cog, main=False):
        if main:
            super().add_cog(cog)
            return

        module = os.path.split(os.path.relpath(inspect.getmodule(cog).__file__, "./modules"))[0]

        try:
            if self.module_config[module]["cogs"][cog.__cog_name__]:
                super().add_cog(cog)
        except KeyError:
            self.config.enable_cog(module, cog.__cog_name__)
            super().add_cog(cog)
