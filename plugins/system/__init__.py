__plugin_meta__ = {
    "name": "System Plugins",
    "authors": ["iDarkLightning"],
    "description": "A set of plugins to interface with and control the bot. The settings managed by these plugins cannot be disabled",
}

from plugins.system.error_handler import ErrorHandler
from plugins.system.help_command import HelpCommand
from plugins.system.settings.settings import Settings
from plugins.system.admin import AdminCommands
from plugins.system.token_command import TokenCommand


def setup(bot):
    bot.add_cog(Settings)
    bot.add_cog(AdminCommands)
    bot.add_cog(TokenCommand)
    bot.add_cog(HelpCommand)
    bot.add_cog(ErrorHandler)