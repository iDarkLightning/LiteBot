from discord.ext import commands

class RoleConverter(commands.Converter):
    """
    Takes the name of a role, and retunrs a list of all the roles matching that name within the guild
    """
    async def convert(self, ctx: commands.Context, argument: str):
        roles = list(filter(lambda r: r.name.lower() == argument.lower(), ctx.guild.roles))
        if len(roles) == 0:
            raise commands.RoleNotFound

        return roles