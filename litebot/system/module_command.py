from typing import Tuple
from discord.ext import commands
from litebot.system.common import config_view, config_save
from litebot.system.converters import JSONConverter
from litebot.utils import embeds
from litebot.utils.fmt_strings import MODULE_CONFIG_PATH, MODULE_PATH, MODULE_LOADING, CODE_BLOCK, COG_LOADING


class ModuleCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="module")
    async def _module(self, ctx: commands.Context) -> None:
        """
        The root command for the module group
        :param ctx: The context that the command is being executed in
        :type ctx: commands.Context
        """
        if ctx.invoked_subcommand is None:
            pass

    @_module.command(name="view")
    async def _module_view(self, ctx: commands.Context) -> None:
        """
        Allows you to view a list of the available modules
        :param ctx: The context that the command is being executed in
        :type ctx: commands.Context
        """
        await ctx.send(CODE_BLOCK.format("py", "\n".join(self.bot.module_config.keys())))

    @_module.command(name="enable", aliases=["load"])
    async def _module_enable(self, ctx: commands.Context, module: str) -> None:
        """
        Lets the user enable a module
        :param ctx: The context that the command is being executed in
        :type ctx: commands.Context
        :param module: The module to enable
        :type module: str
        """
        try:
            self.bot.module_config.toggle_module(module, True)
            self.bot.load_extension(MODULE_PATH.format(module))
            self.bot.logger.info(MODULE_LOADING.format("Loaded", module))
            await ctx.send(embed=embeds.SuccessEmbed(MODULE_LOADING.format("Loaded", module)))
        except ModuleNotFoundError:
            await ctx.send(embed=embeds.ErrorEmbed(f"There is no module matching: {module}"))
        except Exception as e:
            self.bot.logger.exception("Error in loading module", exc_info=e)
            await ctx.send(embed=embeds.ErrorEmbed(f"Error in loading module: {e}"))

    @_module.command(name="disable", aliases=["unload"])
    async def _module_disable(self, ctx: commands.Context, module: str) -> None:
        """
        Lets the user disable a module
        :param ctx: The context that command is being executed in
        :type ctx: commands.Context
        :param module: The module to disable
        :type module: str
        """
        try:
            self.bot.module_config.toggle_module(module, False)
            self.bot.unload_extension(MODULE_PATH.format(module))
            self.bot.logger.info(MODULE_LOADING.format("Unloaded", module))
            await ctx.send(embed=embeds.SuccessEmbed(MODULE_LOADING.format("Unloaded", module)))
        except ModuleNotFoundError:
            await ctx.send(embed=embeds.ErrorEmbed(f"There is no module matching: {module}"))
        except Exception as e:
            self.bot.logger.exception("Error in loading module", exc_info=e)
            await ctx.send(embed=embeds.ErrorEmbed(f"Error in loading module: {e}"))

    @_module.command(name="reload")
    async def _module_reload(self, ctx: commands.Context, module: str) -> None:
        """
        Lets the user reload a module
        :param ctx: The context that command is being executed in
        :type ctx: commands.Context
        :param module: The module to disable
        :type module: str
        """
        try:
            self.bot.reload_extension(MODULE_PATH.format(module))
            self.bot.logger.info(MODULE_LOADING.format("Reloaded", module))
            await ctx.send(embed=embeds.SuccessEmbed(MODULE_LOADING.format("Reloaded", module)))
        except Exception as e:
            self.bot.logger.exception("Error in loading module", exc_info=e)
            await ctx.send(embed=embeds.ErrorEmbed(f"Error in loading module: {e}"))

    @_module.group(name="config")
    async def _config(self, ctx: commands.Context) -> None:
        """
        The root command for the config subgroup
        of the module group
        :param ctx: The context that the command is being executed in
        :type ctx: commands.Context
        """
        if ctx.invoked_subcommand is None:
            pass

    @_config.command(name="view")
    async def _config_view(self, ctx: commands.Context, module: str, *subs: Tuple[str]) -> None:
        """
        Allows you to view the config for a module
        :param ctx: The context that the ocmmand was being executed in
        :type ctx: commands.Context
        :param module: The module to view the config for
        :type module: str
        :param subs: Any subpath to view within the config
        :type subs: Tuple[str]
        """
        try:
            await config_view(self.bot.module_config[module]["config"], ctx, subs)
        except KeyError:
            await ctx.send(embed=embeds.ErrorEmbed(f"There is no module matching: {module}"))

    @_config.command(name="set")
    async def _config_set(self, ctx: commands.Context, module: str, key: str, *, value: JSONConverter) -> None:
        """
        Allows to set the value of a config field
        :param ctx: The context with which the command is being invoked
        :type ctx: commands.Context
        :param module: The module to set the config for
        :type module: str
        :param key: The key to set
        :type key: str
        :param value: The value to set it to
        :type value: str
        """
        await config_save(self.bot.module_config, ctx, MODULE_CONFIG_PATH.format(module, key), value)

    @_module.group(name="cogs")
    async def _cogs(self, ctx: commands.Context) -> None:
        """
        The cogs subcommand group for the module command
        :param ctx: The context the command is being executed in
        :type ctx: commands.Context
        """
        if ctx.invoked_subcommand is None:
            pass

    @_cogs.command(name="view")
    async def _cog_view(self, ctx: commands.Context, module: str) -> None:
        """
        Lets the user view all the cogs for a certain module
        :param ctx: The context the command is being executed in
        :type ctx: commands.Context
        :param module: The module to view the cogs for
        :type module: str
        """
        await ctx.send(CODE_BLOCK.format("py", "\n".join(self.bot.module_config[module]["cogs"].keys())))

    @_cogs.command(name="enable", aliases=["load"])
    async def _cog_enable(self, ctx: commands.Context, module: str, cog_name: str) -> None:
        """
        Lets the user enable a cog for a module
        :param ctx: The context that the command is being executed in
        :type ctx: commands.Context
        :param module: The module that the cog is a part of
        :type module: str
        :param cog_name: The name of the cog
        :type cog_name: str
        """
        try:
            self.bot.module_config.toggle_cog(module, cog_name, True)
            self.bot.reload_extension(MODULE_PATH.format(module))
            self.bot.logger.info(COG_LOADING.format("Loaded", cog_name, module))
            await ctx.send(embed=embeds.SuccessEmbed(COG_LOADING.format("Loaded", cog_name, module)))
        except ModuleNotFoundError:
            await ctx.send(embed=embeds.ErrorEmbed(f"There is no module matching: {module}"))
        except Exception as e:
            self.bot.logger.exception("Error in loading cog", exc_info=e)
            await ctx.send(embed=embeds.ErrorEmbed(f"Error in loading cog: {e}"))

    @_cogs.command(name="disable", aliases=["unload"])
    async def _cog_disable(self, ctx: commands.Context, module: str, cog_name: str):
        """
        Lets the user disable a cog for a module
        :param ctx: The context that command is being executed in
        :type ctx: commands.Context
        :param module: The module that the cog is a part of
        :type module: str
        :param cog_name: The name of the cog
        :type cog_name: str
        """
        try:
            self.bot.module_config.toggle_cog(module, cog_name, False)
            self.bot.reload_extension(MODULE_PATH.format(module))
            self.bot.logger.info(COG_LOADING.format("Unloaded", cog_name, module))
            await ctx.send(embed=embeds.SuccessEmbed(COG_LOADING.format("Unloaded", cog_name, module)))
        except ModuleNotFoundError:
            await ctx.send(embed=embeds.ErrorEmbed(f"There is no module matching: {module}"))
        except Exception as e:
            self.bot.logger.exception("Error in loading cog", exc_info=e)
            await ctx.send(embed=embeds.ErrorEmbed(f"Error in loading cog: {e}"))

