import abc

from litebot.errors import ArgumentError
from litebot.minecraft.commands.context import ServerCommandContext


class ArgumentType(abc.ABC):
    REPR = "StringArgument"

    @abc.abstractmethod
    def __init__(self, val, expected_type):
        if not isinstance(val, expected_type):
            raise ArgumentError(f"Expected type {expected_type}! Received type: {val}")

        self.val = val

class StringArgumentType(ArgumentType):
    def __init__(self, val: str = None) -> None:
        if val:
            super().__init__(val, str)

class MessageArgumentType(StringArgumentType, str):
    REPR = "MessageArgument"

class IntegerArgumentType(ArgumentType, int):
    REPR = "IntegerArgument"

    def __init__(self, val: int):
        super().__init__(val, int)

class BooleanArgumentType(ArgumentType ):
    REPR = "BooleanArgument"

    def __init__(self, val: bool):
        super().__init__(val, bool)

class Suggester(StringArgumentType, abc.ABC):
    REPR = "SuggesterArgument"

    @abc.abstractmethod
    async def suggest(self, ctx: ServerCommandContext, arg: str, prior_args: dict) -> list:
        pass

class StrictSuggester(Suggester, abc.ABC):
    REPR = "StrictSuggesterArgument"
