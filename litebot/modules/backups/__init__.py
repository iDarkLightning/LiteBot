from .backups import BackupsCommand


def setup(bot):
    bot.add_cog(BackupsCommand(bot))

def config(bot):
    return {
        "backup_role": []
    }

def requirements(bot):
    for server in bot.servers.all:
        if server.server_dir:
            return True

    return False