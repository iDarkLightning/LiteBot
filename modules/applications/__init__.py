from . import apps, ticket_commands

def setup(bot):
    bot.load_cog('applications', apps.Applications(bot))
    bot.load_cog('applications', ticket_commands.TicketCommands(bot))

def config():
    apps_config = {
        "spreadsheet_url": "",
        "applications_category": 1,
        "archives_category": 1,
        "discord_name_question": "",
        "voting_channel": 1
    }
    return apps_config