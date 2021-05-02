from os import path, getcwd
from gspread import service_account

from litebot.litebot import LiteBot
from . import apps, ticket_commands

MODULE_NAME = "applications"

def setup(bot):
    account = service_account(path.join(getcwd(), "litebot", "modules", MODULE_NAME, "creds.json"))
    bot.add_cog(apps.Applications(bot, account), MODULE_NAME)
    bot.add_cog(ticket_commands.TicketCommands(bot, account), MODULE_NAME)

def config(bot):
    return {
        "spreadsheet_url": "",
        "discord_name_question": "",
        "applications_category": 0,
        "voting_channel": 0,
        "verify_channel": 0,
        "vouch_expire_time": {
            "weeks": 0,
            "days": 0,
            "hours": 0,
            "minutes": 0,
            "seconds": 0
        }
    }

def requirements(bot: LiteBot):
    config_ = bot.module_config["applications"]["config"]
    config_met = config_["spreadsheet_url"] and config_["applications_category"] and config_["voting_channel"] and\
                 config_["verify_channel"] and config_["discord_name_question"]

    return config_met and path.exists(path.join(getcwd(), "litebot", "modules", MODULE_NAME, "creds.json"))