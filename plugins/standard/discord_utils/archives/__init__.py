__plugin_meta__ = {
    "name": "Archives",
    "description": "Archive discord channels to the bot's database, and provide an API to access these channels",
    "authors": ["iDarkLightning"]
}

from plugins.standard.discord_utils.archives.archive_command import ArchiveCommand
from plugins.standard.discord_utils.archives.archive_route import blueprint


def setup(bot):
    bot.add_cog(ArchiveCommand)
    bot.server.blueprint(blueprint)