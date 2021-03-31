from . import auto_role, list_command, moderator_commands, timezone_command
from .polls import poll_command

MODULE_NAME = "discord_utils"

def config(bot):
    return {
        "auto_role_id": 0,
        "mute_role_id": 0
    }

def setup(bot):
    bot.add_cog(auto_role.AutoRole(bot, MODULE_NAME))
    bot.add_cog(list_command.ListCommand(bot, MODULE_NAME))
    bot.add_cog(moderator_commands.ModeratorCommands(bot, MODULE_NAME))
    bot.add_cog(timezone_command.TimezoneCommand(bot, MODULE_NAME))
    bot.add_cog(poll_command.PollCommand(bot))