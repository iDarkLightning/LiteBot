from typing import List
import discord
from discord.ext import commands

class RoleConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        roles = list(filter(lambda r: r.name.lower() == argument.lower(), ctx.guild.roles))
        if len(roles) == 0:
            raise commands.RoleNotFound

        return roles