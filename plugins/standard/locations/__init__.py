__plugin_meta__ = {
    "name": "Locations",
    "description": "Serverside Locations Manager!",
    "authors": ["iDarkLightning"]
}

from plugins.standard.locations.location_command import LocationCommand


def setup(bot):
    bot.add_cog(LocationCommand)
