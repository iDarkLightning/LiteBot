from . import discord_bridge, server_bridge


def setup(bot):
    bot.add_cog(server_bridge.ServerBridge(bot))
    bot.add_cog(discord_bridge.DiscordBridge(bot))

def config(bot):
    return {
        "incoming_messages": "",
        "outgoing_messages": ""
    }

# def requirements(bot):
#     for server in bot.servers.get_all_instances():
#         if server.connected:
#             return True