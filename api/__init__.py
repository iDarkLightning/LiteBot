from .webserver import WebServer

def setup(bot):
    bot.add_cog(WebServer(bot, bot.config["api_server"]["port"]), main=True)