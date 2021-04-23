from __future__ import annotations
import asyncio
import inspect
from typing import List, Callable, Tuple, Any, Optional, get_type_hints, get_args, Union, Type
from litebot.errors import ServerActionNotFound, InvalidEvent, ArgumentError
from litebot.minecraft.commands.arguments import ArgumentType, Suggester
from litebot.minecraft.commands.context import ServerCommandContext

def _build_args(func: Callable) -> Union[
    tuple[list, dict], tuple[list[dict[str, Union[bool, Any]]], dict[Any, Type[Suggester]], list[Type[ArgumentType]]]]:
    arg_hints = {k: v for k, v in get_type_hints(func).items() if k != "return" and v is not ServerCommandContext}
    if not arg_hints:
        return [], {}, []

    args = []
    arg_types = []
    suggestors = {}
    started_optional = False

    for arg_name, arg_type in arg_hints.items():
        generic_args = get_args(arg_type)
        arg_type = generic_args[0] if generic_args else arg_type

        if not issubclass(arg_type, ArgumentType) or (started_optional and not generic_args):
            raise ArgumentError("Invalid arguments for server command!")

        if generic_args:
            started_optional = True

        args.append({"name": arg_name, "type": arg_type.REPR, "optional": started_optional})
        arg_types.append(arg_type)

        if issubclass(arg_type, Suggester):
            suggestors[arg_name] = arg_type

    return args, suggestors, arg_types

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
    actions = []

    def __init__(self, func, cog=None, **kwargs):
        super().__init__(func, cog, **kwargs)

        self.is_sub = bool(kwargs.get("is_sub"))
        self.register = bool(kwargs.get("register")) if kwargs.get("register") is not None else True
        self.op_level = kwargs.get("op_level") or 0

        args, suggestors, arg_types = _build_args(func)
        self.arguments = args
        self.suggestors = suggestors
        self.arg_types = arg_types

        self.subs: dict[str, ServerCommand] = {}

    @classmethod
    def get_built(cls):
        return [c.build() for c in cls.actions if not c.is_sub]

    @property
    def help_msg(self) -> Optional[str]:
        """
        The help message for the command
        :return: The command's help message
        :rtype: Optional[str]
        """
        return inspect.getdoc(self.callback)

    def build(self):
        if not self.register:
            return

        data = {"name": self.name, "OPLevel": self.op_level}

        if self.arguments:
            data["arguments"] = self.arguments

        subs = []

        for sub in self.subs.values():
            subs.append(sub.build())

        data["subs"] = subs

        return data

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
            sub_command = ServerCommand(func, is_sub=True, **kwargs)
            self.subs[sub_command.name] = sub_command

            return sub_command

        return decorator

    async def invoke(self, ctx: ServerCommandContext, args: List[Any]) -> None:
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