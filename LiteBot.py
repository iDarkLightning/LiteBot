import discord
from discord.ext import commands
import datetime
from datetime import datetime
from rcon import MCRcon
from utils.config import BotConfig
import sqlite3
import os


class LiteBot(commands.Bot):
    def __init__(self):
        self.config = BotConfig()
        super(LiteBot, self).__init__(command_prefix=self.config['prefix'], intents=discord.Intents.all(),
                                      help_command=None)
        self.token = self.config['token']
        self.module_config = self.config['modules']
        self.servers = self.config.set_servers()
        self.rcons = self.init_rcons()
        self.db = sqlite3.connect('litebot.db')
        self.guild_id = self.config['main_guild_id']
        self.__extensions = {}

    # Loads all available modules if they are enabled in config, else sets config to false
    def init_modules(self):
        self.load_extension('main')
        modules = list(
            filter(lambda path: os.path.isdir(f'./modules/{path}') and path != '__pycache__', os.listdir('./modules')))
        for module in modules:
            try:
                if self.module_config[module]['enabled']:
                    self.load_extension(f'modules.{module}')
            except KeyError:
                print(module)

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
            bridge_channel_id  = self.servers[server]['bridge_channel_id']
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
                print(e)
                await ctx.send(f'An error occuring {action.lower()}ing that module')

    # Loads a cog if is enabled in config
    def load_cog(self, module, cog):
        if module == 'main':
            if self.module_config[module][cog.__cog_name__]:
                super().add_cog(cog)
            return

        try:
            if self.module_config[module]['cogs'][cog.__cog_name__]:
                super().add_cog(cog)
        except KeyError:
            self.config.enable_cog(module, cog.__cog_name__)
            super().add_cog(cog)
