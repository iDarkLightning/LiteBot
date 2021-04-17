from . import discord_bridge, server_bridge
from ...minecraft.server import MinecraftServer


def setup(bot):
    bot.add_cog(server_bridge.ServerBridge(bot))
    bot.add_cog(discord_bridge.DiscordBridge(bot))

def requirements(bot):
    for server in bot.servers.get_all_instances():
        if server.running_lta:
            return True