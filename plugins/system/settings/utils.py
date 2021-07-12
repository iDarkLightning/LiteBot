import json
from typing import Union

from discord.ext import commands

from litebot.core.context import Context
from litebot.utils.fmt_strings import CODE_BLOCK

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
    async def convert(self, ctx: Context, argument: str) -> Union[int, bool, str]:
        if argument.isnumeric():
            return int(argument)
        elif argument.lower() == "true":
            return True
        elif argument.lower() == "false":
            return False

        try:
            return json.loads(argument)
        except (SyntaxError, ValueError):
            return argument

def pretty_json_code(dict_: dict) -> str:
    """
    Convert a dict to readable JSON string inside a code block
    :param dict_: The dict to convert
    :type dict_: dict
    :return: A readable json string
    :rtype: dict
    """

    return CODE_BLOCK.format("json", json.dumps(dict_, indent=4))