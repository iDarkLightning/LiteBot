from .backups import BackupsCommand
from ...minecraft.server import MinecraftServer


def setup(bot):
    bot.add_cog(BackupsCommand(bot))

def config(bot):
    return {
        "backup_role": []
    }

def requirements(bot):
    servers = bot.servers.get_all_instances()
    for server in servers:
        if server.server_dir:
            return True

    return False