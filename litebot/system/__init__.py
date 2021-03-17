from . import config_command, module_command

def setup(bot):
    bot.add_cog(config_command.ConfigCommand(bot), True)
    bot.add_cog(module_command.ModuleCommand(bot), True)