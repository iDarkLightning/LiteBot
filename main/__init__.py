from main import status, tps, server_commands, scoreboard, backups


def setup(bot):
    bot.load_cog('main', status.Status(bot))
    bot.load_cog('main', tps.Tps(bot))
    bot.load_cog('main', server_commands.ServerCommands(bot))
    bot.load_cog('main', scoreboard.ScoreBoard(bot))
    bot.load_cog('main', backups.Backups(bot))
