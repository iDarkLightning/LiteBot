from . import backups

def setup(bot):
    bot.add_cog(backups.Backups(bot))

def config(bot):
    return {server: {"backup_directory": "", "world_directory": ""} for server in bot.servers}