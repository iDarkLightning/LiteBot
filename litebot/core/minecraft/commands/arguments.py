import abc
import json

from litebot.errors import ArgumentError
from litebot.core.minecraft.commands.context import ServerCommandContext
from litebot.core.minecraft.player import Player


class ArgumentType(abc.ABC):
    REPR = "StringArgument"

    @abc.abstractmethod
    def __init__(self, val, expected_type):
        if not isinstance(val, expected_type):
            raise ArgumentError(f"Expected type {expected_type}! Received type: {type(val)}")

        self.val = val

class StringArgumentType(ArgumentType, str):
    def __init__(self, val: str = None) -> None:
        if val:
            ArgumentType.__init__(self, val, str)

class MessageArgumentType(StringArgumentType, str):
    REPR = "MessageArgument"

class IntegerArgumentType(ArgumentType, int):
    REPR = "IntegerArgument"

    def __init__(self, val: int):
        super().__init__(int(val), int)

class BooleanArgumentType(ArgumentType):
    REPR = "BooleanArgument"

    def __init__(self, val: bool):
        super().__init__(val, bool)

class PlayerArgumentType(ArgumentType, Player):
    REPR = "PlayerArgument"

    def __init__(self, val):
        val = Player(**json.loads(val))

        super().__init__(val, Player)

class BlockPosArgumentType(ArgumentType):
    REPR = "BlockPosArgument"

    def __init__(self, val):
        super().__init__(json.loads(val), list)

class DimensionArgumentType(ArgumentType):
    REPR = "DimensionArgument"

    def __init__(self, val):
        super().__init__(val, str)

class Suggester(StringArgumentType, abc.ABC):
    REPR = "SuggesterArgument"

    @abc.abstractmethod
    async def suggest(self, ctx: ServerCommandContext, arg: str, prior_args: dict) -> list:
        pass

class StrictSuggester(Suggester, abc.ABC):
    REPR = "StrictSuggesterArgument"
