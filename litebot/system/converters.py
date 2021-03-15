from typing import Union
from discord.ext import commands

class JSONConverter(commands.Converter):
    """
    A converter that converts strings into JSON values.
    Example Conversions:
    '32' -> 32
    'true' -> True
    'false' -> False
    """
    async def convert(self, ctx: commands.Cog, argument: str) -> Union[int, bool, str]:
        if argument.isnumeric():
            return int(argument)
        elif argument.lower() == "true":
            return True
        elif argument.lower() == "false":
            return False

        return argument