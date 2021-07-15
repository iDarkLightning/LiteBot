from discord.ext import commands

from litebot.core import Cog
from litebot.core.context import Context
from plugins.system.settings.embeds import SettingEmbed, PluginEmbed
from plugins.system.settings.menus import SettingsMenu, PluginsMenu


class Settings(Cog, required=True):
    @commands.command(name="settings")
    @commands.has_permissions(manage_guild=True)
    async def _settings(self, ctx: Context):
        """
        View and configure all the available settings for the bot!
        """
        embeds = []

        for setting in self._bot.settings_manager.settings.values():
            embed = SettingEmbed(setting)
            await embed.add_usable_by(ctx)
            embeds.append(embed)

        menu = SettingsMenu(ctx, embeds)
        await menu.start()

    @commands.command(name="plugins")
    @commands.has_permissions(manage_guild=True)
    async def _plugins(self, ctx: Context):
        """
        View and configure all the available plugins installed on the bot!
        """

        embeds = []

        for plugin in self._bot.plugin_manager.all_plugins.values():
            embed = PluginEmbed(plugin, self._bot)
            await embed.add_usable_by(ctx)
            embeds.append(embed)

        menu = PluginsMenu(ctx, embeds)
        await menu.start()
