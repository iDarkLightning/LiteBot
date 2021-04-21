from __future__ import annotations
import asyncio
import inspect
from typing import List, Callable, Tuple, Any, Optional
from litebot.errors import ServerActionNotFound, InvalidEvent
from litebot.minecraft.server_commands.server_context import ServerCommandContext

class ActionTypes:
    COMMAND = "command"
    EVENT = "event"

class ServerAction:
    """
    A base class for a server command and a server event.
    """
    actions = []

    def __init__(self, func, cog=None, **kwargs) -> None:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine")

        self.name = kwargs.get("name") or func.__name__
        self.callback = func
        self.cog = cog # Will be set manually when adding the cog
        self._register_command(self)

    @classmethod
    def _register_command(cls, instance: ServerAction) -> None:
        """
        Adds the command to an internal list of commands
        :param instance: The command instance
        :type instance: ServerAction
        """
        cls.actions.append(instance)

    @classmethod
    def get_from_name(cls, name: str) -> ServerAction:
        """
        Gets a command from the internal list of commands
        :param name: The name of the command to retrieve
        :type name: str
        :return: The command with the given name
        :rtype: ServerAction
        :raises: ServerActionNotFound
        """
        server = list(filter(lambda s: s.name == name, cls.actions))
        if len(server) > 0:
            return server[0]
        else:
            raise ServerActionNotFound

class ServerCommand(ServerAction):
    def __init__(self, func, cog=None, **kwargs):
        super().__init__(func, cog, **kwargs)
        self.subs: dict[str, ServerCommand] = {}

    @property
    def help_msg(self) -> Optional[str]:
        """
        The help message for the command
        :return: The command's help message
        :rtype: Optional[str]
        """
        return inspect.getdoc(self.callback)

    def sub(self, **kwargs):
        """
        Registers a subcommand for the commnad.
        Works similarly to registering a normal command,
        See `command`.

        Example
        --------
            @command(name="command")
            async def _command(ctx):
                pass

            @_command.sub(name="sub)
            async def _command_sub(ctx):
                pass

        :param kwargs: The additional arguments when registering the command
        :type kwargs: str
        :return: A decorator that registers the subcommand
        :rtype: Callable
        """
        def decorator(func):
            sub_command = ServerCommand(func, **kwargs)
            self.subs[sub_command.name] = sub_command

        return decorator

    async def invoke(self, ctx: ServerCommandContext, args: Tuple[Any]) -> None:
        """
        Invokes the command
        :param ctx: The server that the command is being invoked to
        :type ctx: ServerCommandContext
        :param args: The arguments for the command
        :type args: List[str]
        """
        if self.cog:
            await self.callback(self.cog, ctx, *args)
        else:
            await self.callback(ctx, *args)

class ServerEvent(ServerAction):
    VALID_EVENTS = (
        "on_message"
    )

    def __init__(self, func, cog=None, **kwargs):
        name = kwargs.get("name") or func.__name__

        if name not in ServerEvent.VALID_EVENTS:
            raise InvalidEvent

        super().__init__(func, cog, **kwargs)

    @classmethod
    def get_from_name(cls, name: str) -> List[ServerEvent]:
        """
        Gets a command from the internal list of commands
        :param name: The name of the event to retrieve
        :type name: str
        :return: All the events registed with the name
        :rtype: ServerAction
        :raises: ServerActionNotFound
        """
        server = list(filter(lambda s: s.name == name, cls.actions))
        if len(server) > 0:
            return server
        else:
            raise ServerActionNotFound

    async def invoke(self, payload) -> None:
        """
        Invokes the event
        :param ctx: The server that the event was dispatched from
        :type ctx: ServerEventPayload
        :param args: The arguments for the event
        :type args: List[str]
        """
        if self.cog:
            await self.callback(self.cog, payload)
        else:
            await self.callback(payload)

def command(**kwargs) -> Callable:
    """
    A decorator that will convert a function into
    a ServerCommand object, and effectively
    register the command. This can be used inside or outside of a cog.

    Example
    --------
    .. code-block :: python3
        # Note that if `name` overrides the function name, which will be the default name
        @command(name="test")
        async def command(ctx, arg1):
            ``` (docstring)
            This will be the help message for the command
            ```
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

def event(**kwargs) -> Callable:
    """
    A decorator that will convert a function into
    a ServerEvent object, and effectively
    register the event. This can be used inside or outside of a cog.

    Unlike a command, you can register multiple events with the same name.
    They will all be executed when the event is invoked.

    Example
    --------
    .. code-block :: python3
        # Note that if `name` overrides the function name, which will be the default name
        @event(name="test")
        async def command(ctx, arg1):
            print("Hi There!!!")

    The usage inside a cog will be identical. If used in a cog,
    you will be able to access the Cog object using event.cog

    :param kwargs: The additional arguments when registering the event
    :type kwargs: str
    :return: A decorator that registers the event
    :rtype: Callable
    """
    def decorator(func):
        return ServerEvent(func, **kwargs)

    return decorator