from . import apps, ticket_commands

def setup(bot):
    bot.cog_loader.load(apps.Applications(bot))
    bot.cog_loader.load(ticket_commands.TicketCommands(bot))
