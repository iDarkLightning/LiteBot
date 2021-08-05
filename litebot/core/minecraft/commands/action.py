from __future__ import annotations

import asyncio
import inspect
from typing import List, Callable, Any, Optional, get_type_hints, get_args, Union, Type, TYPE_CHECKING

from litebot.core.minecraft.commands.arguments import ArgumentType, Suggester
from litebot.core.minecraft.commands.context import ServerCommandContext
from litebot.errors import ArgumentError

if TYPE_CHECKING:
    from litebot.core import Setting, Cog
    from litebot.core.minecraft import MinecraftServer
    from litebot.litebot import LiteBot


class ServerCommand:
    __setting__: Setting

    def __init__(self, func: Callable, cog: Optional[Cog] = None, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine")

        self.name = kwargs.get("name") or func.__name__
        self.callback = func
        self.cog = cog  # Will be set manually when adding the cog

        self.parent = kwargs.get("parent")
        self.register = bool(kwargs.get("register")) if kwargs.get("register") is not None else True
        self.op_level = kwargs.get("op_level") or 0
        self.checks: list[Callable] = []
        self.requirements: list[Callable] = []

        self.arguments, self.suggestors, self.arg_types = self._build_args(func)
        self.subs: dict[str, ServerCommand] = {}

    @property
    def help_msg(self) -> Optional[str]:
        """
        Returns:
            The help message for the command
        """
        return inspect.getdoc(self.callback)

    @property
    def full_name(self) -> str:
        """
        Returns:
            The full name of the command
        """
        return ".".join(self._get_full_path()[::-1])

    @property
    def root_parent(self) -> ServerCommand:
        """
        Returns:
            The highest level parent of the command
        """
        cmd = self

        while cmd.parent is not None:
            cmd = cmd.parent

        return cmd

    def build(self) -> Optional[dict[str, Union[str, int, list, dict]]]:
        """Build the command to send to the server.

        Examples:
            {
                "name": "test",
                "OPLevel": 1,
                "arguments": [
                    {
                        "name": "test",
                        "type": "StringArgumentType",
                        "optional": False,
                        "full": "test"
                    }
                ],
                "subs": [
                    {
                        "name": "test",
                        "OPLevel": 1,
                        "arguments": [],
                        "subs": [],
                        "full": "test.test"
                    }
                ]
            }

        Returns:
            The JSON representation of the command that will be sent to the server.
        """
        if not self.register:
            return

        data = {"name": self.name, "OPLevel": self.op_level, "arguments": self.arguments, "full": self.full_name}
        subs = []

        for sub in self.subs.values():
            subs.append(sub.build())

        data["subs"] = subs

        return data

    def update_cog_ref(self, cog: Cog) -> None:
        """Update the command's reference to the cog

        Args:
            cog: The Cog object that the command belongs to
        """
        self.cog = cog

        if self.subs:
            for sub in self.subs.values():
                sub.cog = cog

    def sub(self, **kwargs) -> Callable:
        """Registers a subcommand for the commnad.

        Works similarly to registering a normal command,
        See `command`.

        Examples:
            @command(name="command")
            async def _command(_ctx):
                pass

            @_command.sub(name="sub)
            async def _command_sub(_ctx):
                pass

        Args:
            **kwargs: The additional arguments to use for building the subcommand

        Returns:
            A decorator that will convert a coroutine into a subcommand for this command
        """

        def decorator(func) -> ServerCommand:
            sub_command = ServerCommand(func, parent=self, **kwargs)
            self.subs[sub_command.name] = sub_command

            return sub_command

        return decorator

    def create_context(self, server: MinecraftServer, bot: LiteBot, data: dict) -> ServerCommandContext:
        """Create the context object for this command's execution

        Args:
            server: The server that this command is being executed from
            bot: The Bot object
            data: The data for the command's execution, essentially the arguments that
                were provided to the command

        Returns:
            The command's execution context
        """
        cmd_args = {}
        full_args = data.get("args")

        args = data.get("args", {})
        for arg in self.arguments:
            cmd_args[arg["name"]] = (args.get(arg["name"]))

            if args.get(arg["name"]):
                del args[arg["name"]]

        ctx = ServerCommandContext(self, server, bot, data["player"], args=cmd_args, full_args=full_args)
        return ctx

    async def invoke(self, ctx: ServerCommandContext, args: List[Any]) -> None:
        """Invoke the command

        Args:
            ctx: The context to invoke the command with
            args: The arguments that were provided for the command
        """
        if self.cog:
            await self.callback(self.cog, ctx, *args)
        else:
            await self.callback(ctx, *args)

    def _get_full_path(self) -> list[str]:
        res = [self.name]

        if self.parent:
            res.extend(self.parent._get_full_path())

        return res

    def _build_args(self, func: Callable) -> Union[tuple[list, dict, list], tuple[
        list[dict[str, Union[bool, Any]]], dict[Any, Type[Suggester]], dict[Any, Type[ArgumentType]]]]:
        arg_hints = {k: v for k, v in get_type_hints(func).items() if k != "return" and v is not ServerCommandContext}
        if not arg_hints:
            return [], {}, []

        args = []
        arg_types = {}
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
            arg_types[arg_name] = arg_type

            if issubclass(arg_type, Suggester):
                suggestors[arg_name] = arg_type

        return args, suggestors, arg_types


def command(**kwargs) -> Callable:
    """
    A decorator that will convert a function into
    a ServerCommand object, and effectively
    register the command. This can only be used inside of a cog!
    For registering without a cog, see `LiteBot.server_command`

    Examples:
        # Note that if `name` overrides the function name, which will be the default name
        @command(name="test")
        async def command(_ctx, arg1):
            ``` (docstring)
            This will be the help message for the command
            ```
            print("Hi There!!!")

            await _ctx.send("We executed the command!")

    Args:
        **kwargs: The additional arguments to use for building the subcommand

    Returns:
        A decorator that will convert the coroutine into a ServerCommand object
    """

    def decorator(func) -> ServerCommand:
        return ServerCommand(func, **kwargs)

    return decorator
