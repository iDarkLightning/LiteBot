from . import auto_role, list_command

MODULE_NAME = "discord_utils"

def config(bot):
    return {
        "auto_role_id": 0
    }

def setup(bot):
    bot.add_cog(auto_role.AutoRole(bot, MODULE_NAME))
    bot.add_cog(list_command.ListCommand(bot, MODULE_NAME))