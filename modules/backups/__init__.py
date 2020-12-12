from . import backups

def setup(bot):
    bot.add_cog(backups.Backups(bot))