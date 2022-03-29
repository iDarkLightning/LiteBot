__plugin_meta__ = {
    "name": "Carpet Rules",
    "description": "Get a list of modified carpet rules from the server.",
    "authors": ["Crec0"],
}

from plugins.standard.carpet_rules.carpet_rules import CarpetRulesCommand


def setup(bot):
    bot.add_cog(CarpetRulesCommand, bot)
