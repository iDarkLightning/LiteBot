from main import status, tps, server_commands, scoreboard


def setup(bot):
    bot.add_cog(status.Status(bot), True)
    bot.add_cog(tps.Tps(bot), True)
    bot.add_cog(server_commands.ServerCommands(bot), True)
    bot.add_cog(scoreboard.ScoreBoard(bot), True)
