import re

from discord.ext import commands


class RoleConverter(commands.Converter):
    """
    Takes a regex expression, and retunrs a list of all the roles matching that regex within the guild
    """
    async def convert(self, ctx: commands.Context, argument: str):
        roles = list(filter(lambda r: re.match(argument.lower(), r.name.lower()), ctx.guild.roles))
        if len(roles) == 0:
            raise commands.RoleNotFound

        return roles