from typing import Tuple
from discord.ext import commands
from .common import config_view, config_save
from .converters import JSONConverter
from ..checks.confirmation_checks import manage_server_confirmation


class ConfigCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="config")
    @commands.has_permissions(manage_guild=True)
    async def _config(self, ctx: commands.Context) -> None:
        """
        The root command for the config group
        :param ctx: The context the command is being executed in
        :type ctx: commands.Context
        """
        if ctx.invoked_subcommand is None:
            pass

    @_config.command()
    @commands.before_invoke(manage_server_confirmation)
    async def view(self, ctx: commands.Context, *subs: Tuple[str]) -> None:
        """
        Lets you view the config. You can specify up to a certain path
        :param ctx: The context the command is being executed in
        :type ctx: commands.Context
        :param subs: The sub paths
        :type subs: Tuple[Any]
        """
        await config_view(self.bot.config, ctx, subs)

    @_config.command()
    async def set(self, ctx: commands.Context, key: str, *, value: JSONConverter) -> None:
        """
        Allows to set the value of a config field
        :param ctx: The context with which the command is being invoked
        :type ctx: commands.Context
        :param key: The key to set
        :type key: str
        :param value: The value to set it to
        :type value: str
        """
        await config_save(self.bot.config, ctx, key, value)
