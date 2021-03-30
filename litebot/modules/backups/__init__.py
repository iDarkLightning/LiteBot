from .backups import BackupsCommand
from ...minecraft.server import MinecraftServer


def setup(bot):
    bot.add_cog(BackupsCommand(bot))

def requirements(bot):
    servers = MinecraftServer.get_all_instances()
    for server in servers:
        if server.server_dir:
            return True

    return False