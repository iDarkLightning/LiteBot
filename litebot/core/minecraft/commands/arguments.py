from __future__ import annotations

import abc
import json
from typing import TYPE_CHECKING

from litebot.errors import ArgumentError
from litebot.core.minecraft import Player

if TYPE_CHECKING:
    from litebot.core.minecraft.commands import ServerCommandContext

class ArgumentType(abc.ABC):
    """Different argument types for server commands.

    In order to implement a new argument type, you must inherit from this class,
    and override the `REPR` class variable with the string representation of the argument
    as implemented in LiteBot-Mod. `StringArgument` by default.
    """
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
    """A suggester argument type.

    You can inherit from this class to implement a Suggester argument type
    that will suggest the values returned by the `suggest` method to the command executor.
    """

    REPR = "SuggesterArgument"

    @abc.abstractmethod
    async def suggest(self, ctx: ServerCommandContext) -> list:
        pass

class StrictSuggester(Suggester, abc.ABC):
    """
    A variation of the Suggester Argument Type that ensures the executor
    selects one of the suggested arguments.
    """
    REPR = "StrictSuggesterArgument"
