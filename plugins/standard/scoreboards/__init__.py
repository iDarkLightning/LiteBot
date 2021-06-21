__plugin_meta__ = {
    "name": "Scoreboards",
    "description": "View the scores for an objective (as displayed in the ingame sidebar) from discord",
    "authors": ["iDarkLightning"]
}

from plugins.standard.scoreboards.scoreboard import Scoreboard


def setup(bot):
    bot.add_cog(Scoreboard, bot)