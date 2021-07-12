__plugin_meta__ = {
    "name": "Server Panel",
    "description": "A game panel to control your servers embedded in discord. (Makes use of LiteHost)",
    "authors": ["iDarkLightning"]
}

from plugins.standard.panel.panel_command import PanelCommand


def setup(bot):
    bot.add_cog(PanelCommand)