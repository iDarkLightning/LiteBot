from discord.ext import commands

from litebot.core import Cog
from litebot.utils.checks.confirmation_checks import manage_server_confirmation
from litebot.modules.system.common import config_view, config_save
from litebot.modules.system.converters import JSONConverter
from litebot.utils import embeds
from litebot.utils.fmt_strings import MODULE_CONFIG_PATH, MODULE_PATH, MODULE_LOADING, CODE_BLOCK, COG_LOADING


class ModuleCommand(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="module")
    @commands.has_permissions(manage_guild=True)
    async def _module(self, ctx: commands.Context) -> None:
        """
        This is the root command for the module group.
        This command serves no function without
        a subcommand, but will send the help message for this group.
        Essentially invokes `help module`
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help("module")

    @_module.command(name="view")
    async def _module_view(self, ctx: commands.Context) -> None:
        """
        This command allows you to view all the modules available to you.
        """
        await ctx.send(CODE_BLOCK.format("py", "\n".join(self.bot.module_config.keys())))

    @_module.command(name="enable", aliases=["load"])
    async def _module_enable(self, ctx: commands.Context, module: str) -> None:
        """
        This command allows you to enable a module
        `module` The name of the module to enable
        """
        try:
            self.bot.module_config.toggle_module(module, True)
            self.bot.load_extension(MODULE_PATH.format(module))

            for server in self.bot.servers:
                await server.send_command_tree()

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
        This command allows you to disable a module
        `module` The name of the module to disable
        """
        try:
            self.bot.module_config.toggle_module(module, False)
            self.bot.unload_extension(MODULE_PATH.format(module))

            for server in self.bot.servers:
                await server.send_command_tree()

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
        This command allows you to reload a module
        `module` The name of the module to reload
        """
        try:
            self.bot.reload_extension(MODULE_PATH.format(module))

            for server in self.bot.servers:
                await server.send_command_tree()

            self.bot.logger.info(MODULE_LOADING.format("Reloaded", module))
            await ctx.send(embed=embeds.SuccessEmbed(MODULE_LOADING.format("Reloaded", module)))
        except Exception as e:
            self.bot.logger.exception("Error in loading module", exc_info=e)
            await ctx.send(embed=embeds.ErrorEmbed(f"Error in loading module: {e}"))

    @_module.group(name="config")
    async def _config(self, ctx: commands.Context) -> None:
        """
        This is the root command for the module config subgroup.
        This command serves no function without
        a subcommand, but will send the help message for this group.
        Essentially invokes `help module config`
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help("module config")

    @_config.command(name="view")
    @commands.before_invoke(manage_server_confirmation)
    async def _config_view(self, ctx: commands.Context) -> None:
        """
        This command lets you view the config for a specified module.
        `module` The module to view the config for
        `subs` The subkeys to view in the module
        """
        await config_view(self.bot.module_config, ctx)

    @_config.command(name="set")
    async def _config_set(self, ctx: commands.Context, module: str, key: str, *, value: JSONConverter) -> None:
        """
        This command allows you to set a specific key to a value in the module's config.
        `module` The module that you are setting the config for
        `key` The key to set in the config
        `value` The value to set the key to
        """
        await config_save(self.bot.module_config, ctx, MODULE_CONFIG_PATH.format(module, key), value)

    @_module.group(name="cogs")
    async def _cogs(self, ctx: commands.Context) -> None:
        """
        This is the root command for the module cogs subgroup.
        This command serves no function without
        a subcommand, but will send the help message for this group.
        Essentially invokes `help module cogs`
        """
        if ctx.invoked_subcommand is None:
            pass

    @_cogs.command(name="view")
    async def _cog_view(self, ctx: commands.Context, module: str) -> None:
        """
        This command allows you to view all the
        cogs available in the module.
        `module` The module to view the cogs for
        """
        await ctx.send(CODE_BLOCK.format("py", "\n".join(self.bot.module_config[module]["cogs"].keys())))

    @_cogs.command(name="enable", aliases=["load"])
    async def _cog_enable(self, ctx: commands.Context, module: str, cog_name: str) -> None:
        """
        This command allows you to enable a cog for a module
        `module` The name of the module that the cog is in
        `cog_name` The name of the cog to enable
        """
        try:
            self.bot.module_config.toggle_cog(module, cog_name, True)
            self.bot.reload_extension(MODULE_PATH.format(module))

            for server in self.bot.servers:
                await server.send_command_tree()

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
        This command allows you to disable a cog for a module
        `module` The name of the module that the cog is in
        `cog_name` The name of the cog to disable
        """
        try:
            self.bot.module_config.toggle_cog(module, cog_name, False)
            self.bot.reload_extension(MODULE_PATH.format(module))

            for server in self.bot.servers:
                await server.send_command_tree()

            self.bot.logger.info(COG_LOADING.format("Unloaded", cog_name, module))
            await ctx.send(embed=embeds.SuccessEmbed(COG_LOADING.format("Unloaded", cog_name, module)))
        except ModuleNotFoundError:
            await ctx.send(embed=embeds.ErrorEmbed(f"There is no module matching: {module}"))
        except Exception as e:
            self.bot.logger.exception("Error in loading cog", exc_info=e)
            await ctx.send(embed=embeds.ErrorEmbed(f"Error in loading cog: {e}"))

