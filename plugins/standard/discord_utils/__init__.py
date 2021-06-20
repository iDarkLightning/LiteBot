__plugin_meta__ = {
    "name": "Discord Utilities!",
    "description": "A set of utilites for discord",
    "authors": ["iDarkLightning"]
}

from plugins.standard.discord_utils.auto_role import AutoRole
from plugins.standard.discord_utils.list_command import ListCommand
from plugins.standard.discord_utils.polls import PollCommand
from plugins.standard.discord_utils.timezones import TimezoneCommand


def setup(bot):
    bot.add_cog(TimezoneCommand())
    bot.add_cog(AutoRole())
    bot.add_cog(ListCommand())
    bot.add_cog(PollCommand())