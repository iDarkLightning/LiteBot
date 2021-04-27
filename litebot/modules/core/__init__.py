from . import status_command, server_command, scoreboard_command

def setup(bot):
    bot.add_cog(status_command.StatusCommand(bot), True)
    bot.add_cog(server_command.ServerCommands(bot), True)
    bot.add_cog(scoreboard_command.ScoreboardCommand(bot), True)