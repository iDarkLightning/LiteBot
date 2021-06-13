from typing import Union
from discord.ext import commands
from ast import literal_eval

class JSONConverter(commands.Converter):
    """
    A converter that converts strings into JSON values.
    Example Conversions:
    '32' -> 32
    'true' -> True
    'false' -> False
    '{"key": "value"}' -> {key: value}
    '[1, 2, 3]' -> [1, 2]
    """
    async def convert(self, ctx: commands.Context, argument: str) -> Union[int, bool, str]:
        if argument.isnumeric():
            return int(argument)
        elif argument.lower() == "true":
            return True
        elif argument.lower() == "false":
            return False

        try:
            return literal_eval(argument)
        except (SyntaxError, ValueError):
            return argument