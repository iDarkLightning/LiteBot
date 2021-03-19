from . import status_command, tps_command

def setup(bot):
    bot.add_cog(status_command.StatusCommand(bot), True)
    bot.add_cog(tps_command.TPSCommand(bot), True)