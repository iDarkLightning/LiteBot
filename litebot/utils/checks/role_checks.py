from discord.ext import commands
from discord.utils import get

def config_role_check(config_role: str) -> commands.check:
    """
    A check to see if the user performing a command has the given role from the config
    :param config_role: The name of the role as set in the config
    :type config_role: str
    :return: A check to see if the user meets the criteria
    :rtype: commands.check
    """
    def predicate(ctx, *args, **kwargs):
        bot = ctx.bot
        required_roles = [get(ctx.author.guild.roles, id=role) for role in bot.config[config_role]]
        if not any(role in required_roles for role in ctx.author.roles):
            raise commands.CheckFailure
        return True
    return commands.check(predicate)

def module_config_role_check(config_role: str, module_name: str) -> commands.check:
    """
    A check to see if the user performing a command has the given role from a module's config
    :param config_role: The name of the role in the module's config
    :type config_role: str
    :param module_name: The name of the module that the role is specified in
    :type module_name: str
    :return: A check to see if the user meets the criteria
    :rtype: commands.check
    """
    def predicate(ctx, *args, **kwargs):
        bot = ctx.bot
        required_roles = [get(ctx.author.guild.roles, id=role) for role in bot.module_config[module_name]["config"][config_role]]
        if not any(role in required_roles for role in ctx.author.roles):
            raise commands.CheckFailure
        return True
    return commands.check(predicate)