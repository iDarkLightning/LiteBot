from . import apps, ticket_commands
import os

def setup(bot):
    bot.add_cog(apps.Applications(bot))
    bot.add_cog(ticket_commands.TicketCommands(bot))

def requirements(bot):
    return len(bot.module_config['applications']['spreadsheet_url']) > 1 and os.path.exists("./creds.json")

config = {
        "spreadsheet_url": "",
        "applications_category": 1,
        "archives_category": 1,
        "discord_name_question": "",
        "voting_channel": 1
    }