from . import chatbridge

def setup(bot):
    bot.add_cog(chatbridge.ChatBridge(bot))

def config(bot):
    config_template = {server: {"lta_server_address": ""} for server in bot.servers}
    config_template["litebot_token"] = ""

    return config_template