from discord.ext import commands
from discord.utils import get

def config_role_check(config_role):
    def predicate(ctx, *args, **kwargs):
        bot = ctx.bot
        required_roles = [get(ctx.author.guild.roles, id=role) for role in bot.config[config_role]]
        if not any(role in required_roles for role in ctx.author.roles):
            raise commands.CheckFailure
        return True
    return commands.check(predicate)