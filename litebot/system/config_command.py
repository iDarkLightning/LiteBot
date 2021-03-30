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
        This is the root command for the config group.
        This command serves no function without
        a subcommand, but will send the help message for this group.
        Essentially invokes `help config`
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help("config")

    @_config.command()
    @commands.before_invoke(manage_server_confirmation)
    async def view(self, ctx: commands.Context, *subs: Tuple[str]) -> None:
        """
        This command lets you view the main config for the bot.
        `subs` The subkeys to view in the config
        """
        await config_view(self.bot.config, ctx, subs)

    @_config.command()
    async def set(self, ctx: commands.Context, key: str, *, value: JSONConverter) -> None:
        """
        This command allows you to set a specific key to a value in the bot's config.
        `key` The key to set in the config
        `value` The value to set the key to
        """
        await config_save(self.bot.config, ctx, key, value)
