__plugin_meta__ = {
    "name": "Applications",
    "description": "Take responses from a google form and create a ticket channel for each response",
    "authors": ["iDarkLightning"]
}

import os

from plugins.standard.applications.apps import Applications


def setup(bot):
    bot.add_cog(Applications, os.path.join(os.getcwd(), __name__.replace(".", "/"), "creds.json"))

def requirements(bot):
    return os.path.exists(os.path.join(os.getcwd(), __name__.replace(".", "/"), "creds.json"))

def config(bot):
    return {
        "spreadsheet_url": "",
        "discord_name_question": "",
        "applications_category": 0,
        "voting_channel": 0,
        "verify_channel": 0,
        "required_vouches": 0,
        "vouch_expire_time": {
            "weeks": 0,
            "days": 0,
            "hours": 48,
            "minutes": 0,
            "seconds": 0
        },
        "vote_yes_emoji": "☑️",
        "vote_no_emoji": "❌"
    }