from .backups import BackupsCommand

def setup(bot):
    bot.add_cog(BackupsCommand(bot))