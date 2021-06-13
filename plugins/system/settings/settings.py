from discord.ext import commands

from litebot.core import Cog
from litebot.core.context import Context
from plugins.system.settings.embeds import SettingEmbed
from plugins.system.settings.menus import SettingsMenu

class Settings(Cog, required=True):
    @commands.command(name="settings")
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
