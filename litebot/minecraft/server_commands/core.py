from __future__ import annotations
import asyncio
from typing import List, Callable, Tuple, Any
from litebot.errors import ServerCommandNotFound
from litebot.minecraft.server_commands.server_context import ServerContext


class ServerCommand:
    commands = []

    def __init__(self, func, cog=None, **kwargs) -> None:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine")

        self.name = kwargs.get("name") or func.__name__
        self.help_msg = kwargs.get("help")
        self.callback = func
        self.cog = cog # Will be set manually when adding the cog
        self._register_command(self)

    @classmethod
    def _register_command(cls, instance: ServerCommand) -> None:
        """
        Adds the command to an internal list of commands
        :param instance: The command instance
        :type instance: ServerCommand
        """
        cls.commands.append(instance)

    @classmethod
    def get_from_name(cls, name: str) -> ServerCommand:
        """
        Gets a command from the internal list of commands
        :param name: The name of the command to retrieve
        :type name: str
        :return: The command with the given name
        :rtype: ServerCommand
        :raises: ServerCommandNotFound
        """
        server = list(filter(lambda s: s.name == name, cls.commands))
        if len(server) > 0:
            return server[0]
        else:
            raise ServerCommandNotFound

    async def invoke(self, ctx: ServerContext, args: Tuple[Any]) -> None:
        """
        Invokes the command
        :param ctx: The server that the command is being invoked to
        :type ctx: ServerCommand
        :param args: The arguments for the command
        :type args: List[str]
        """
        await self.callback(ctx, *args)

def server_command(**kwargs) -> Callable:
    """
    A decorator that will convert a function into
    a ServerCommand object, and effectively
    register the command. This can be used inside or outside of a cog.

    Example
    --------
    .. code-block :: python3
        # Note that if `name` overrides the function name, which will be the default name
        @server_command(name="test", help="This prints to the screen")
        async def command(ctx, arg1):
            print("Hi There!!!")

            await ctx.send("We executed the command!")

    The usage inside a cog will be identical. If used in a cog,
    you will be able to access the Cog object using command.cog

    :param kwargs: The additional arguments when registering the command
    :type kwargs: str
    :return: A decorator that registers the command
    :rtype: Callable
    """
    def decorator(func):
        return ServerCommand(func, **kwargs)

    return decorator