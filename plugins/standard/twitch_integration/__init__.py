__plugin_meta__ = {
    "name": "Twitch Chat Integration",
    "description": "Server side commands to stream the live chat from a twitch channel in game",
    "authors": ["iDarkLightning"]
}

from plugins.standard.twitch_integration.chat import TwitchChat


def config(bot):
    return {
        "token": "",
        "nick": "THIS NEEDS TO BE YOUR ACCOUNT NAME",
        "client_id": ""
    }

def setup(bot):
    return bot.add_cog(TwitchChat)