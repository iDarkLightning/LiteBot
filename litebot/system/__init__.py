from .config_command import ConfigCommand

def setup(bot):
    bot.add_cog(ConfigCommand(bot), True)