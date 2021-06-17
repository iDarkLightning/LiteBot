__plugin_meta__ = {
    "name": "Backups",
    "description": "Backup Management for your servers!",
    "authors": ["iDarkLightning"]
}

from plugins.standard.backups.backup_route import blueprint
from plugins.standard.backups.backups import BackupsCommand


def setup(bot):
    bot.add_cog(BackupsCommand())
    bot.server.blueprint(blueprint)