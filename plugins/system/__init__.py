__plugin_meta__ = {
    "name": "System Plugins",
    "authors": ["iDarkLightning"],
    "description": "A set of plugins to interface with and control the bot. The settings managed by these plugins cannot be disabled",
}

from plugins.system.settings.settings import Settings
from plugins.system.admin import AdminCommands

def setup(bot):
    bot.add_cog(Settings)
    bot.add_cog(AdminCommands)