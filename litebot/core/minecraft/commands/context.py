from __future__ import annotations

import abc
import json
from typing import TYPE_CHECKING, Optional

from litebot.core.minecraft import Player
from litebot.core.minecraft.text import Text

if TYPE_CHECKING:
    from litebot.core.minecraft.commands import ServerCommand
    from litebot.litebot import LiteBot
    from litebot.core.minecraft import MinecraftServer
    from litebot.core import Setting

class ServerContext(abc.ABC):
    """
    An abstract context class for interacting with various methods executing from the server.
    """
    def __init__(self, server: MinecraftServer, bot: LiteBot) -> None:
        self.server = server
        self.bot = bot

class ServerCommandContext(ServerContext):
    def __init__(self, command: ServerCommand, server: MinecraftServer, bot: LiteBot, player_data: str, **kwargs) -> None:
        """A context object for a ServerCommand.

        Enables you to access data for the command execution.

        Args:
            command: The command that is being executed
            server: The server the command is being executed from
            bot: The bot object
            player_data: The data for the player who executed the command
            **kwargs: Additional arguments for the command
        """

        super().__init__(server, bot)
        self.command = command
        self.cog = command.cog
        self.args = kwargs["args"]
        self.full_args = kwargs["full_args"]
        self.player = Player(**json.loads(player_data))
        self.after_invoke_args = {}

    @property
    def setting(self) -> Optional[Setting]:
        """
        Returns:
           The setting object for the command
        """
        if self.command is None:
            return None

        try:
            return self.command.__setting__
        except AttributeError:
            return self.command.root_parent.__setting__

    @property
    def config(self) -> Optional[dict]:
        """
        Returns:
            The config for the command
        """
        if self.setting is None:
            return None
        return self.setting.config

    def __setitem__(self, key, value):
        self.after_invoke_args[key] = value

    async def invoke(self):
        """
        Invoke the command with this context
        """
        args = [self.command.arg_types[name](arg).val for name, arg in self.args.items() if arg is not None]

        await self.command.invoke(self, args)

    async def send(self, message=None, text: Text = None) -> None:
        """Enables us to easily send messages to the command executor.

        Sends a message to the player who executed the command

        Args:
            message: The message to send to the server
            text: The `Text` object to the server, should be used for more complex messages.
        """

        if not text:
            text = Text.from_str(message)

        await self.server.send_message(text=text, player=self.player)

class ServerEventContext(ServerContext):
    """A context object for a Server Event.

    Enables you to access data for the event that was dispatched.

    Args:
        server: The server the command is being executed from
        bot: The bot object
        player_data: The data for the player who executed the command
    """

    def __init__(self, server: MinecraftServer, bot: LiteBot, player_data: Optional[str] = None):
        super().__init__(server, bot)
        self.player = Player(**json.loads(player_data)) if player_data else None
        self.setting: Optional[Setting] = None

    def with_setting(self, event):
        """
        Wrap the context with an event setting

        Args:
            event: The event that the setting is sourced for
        """

        self.setting = event.__setting__
        return self

class RPCContext(ServerContext):
    """A context object for a RPC method.

    Enables you to access data for the command execution.

    Args:
        server: The server the command is being executed from
        bot: The bot object
        data: The data sent by the server for the RPC method
    """
    def __init__(self, server: MinecraftServer, bot: LiteBot, data: dict):
        super().__init__(server, bot)
        self.data = data
