from . import status_command

def setup(bot):
    bot.add_cog(status_command.StatusCommand(bot), True)