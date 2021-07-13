from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional

from litebot.core.minecraft import Player
from litebot.core.minecraft.text import Text

if TYPE_CHECKING:
    from litebot.core.minecraft.commands import ServerCommand
    from litebot.litebot import LiteBot
    from litebot.core.minecraft import MinecraftServer
    from litebot.core import Setting

class ServerContext:
    def __init__(self, server: MinecraftServer, bot: LiteBot) -> None:
        self.server = server
        self.bot = bot

class ServerCommandContext(ServerContext):
    """
    A context object for a ServerCommand.
    Lets us easily interact with both the server and the bot
    through a single object.

    :param server: The server that the command is being executed to
    :type server: MinecraftServer
    :param bot: The bot that the command is registered to
    :type bot: LiteBot
    :param player_data: The data for the player that executed the command
    :type player_data: str
    """
    def __init__(self, command: ServerCommand, server: MinecraftServer, bot: LiteBot, player_data: str, **kwargs) -> None:
        super().__init__(server, bot)
        self.command = command
        self.cog = command.cog
        self.after_invoke_args = {}
        self.args = kwargs["args"]
        self.full_args = kwargs["full_args"]
        self.player = Player(**json.loads(player_data))

    @property
    def setting(self) -> Optional[Setting]:
        """
        The setting for the command
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
        """
        Enables us to easily send messages to the server
        from our command
        :param message: The message to send
        :type message: str
        :param text: A keyword argument for the text to send to the server
        :type text: litebot.minecraft.text.Text
        """
        if not text:
            text = Text.from_str(message)

        await self.server.send_message(text=text, player=self.player)

class ServerEventContext(ServerContext):
    """
    A context object for a ServerEvent.
    Lets us easily interact with both the server and the bot
    through a single object.

    :param server: The server that the event was dispatched from
    :type server: MinecraftServer
    :param bot: The bot that the event is registered for
    :type bot: LiteBot
    :param player_data: If the event is related to a player, then the data for that player
    :type player_data: Optional[str]
    """
    def __init__(self, server, bot, player_data=Optional[str]):
        super().__init__(server, bot)
        self.player = Player(**json.loads(player_data)) if player_data else None
        self.setting: Optional[Setting] = None

    def with_setting(self, event):
        self.setting = event.__setting__
        return self

class RPCContext(ServerContext):
    """
    A context object for a RPC Handler.
    Lets us easily interact with both the server and the bot
    through a single object.

    :param server: The server that the remote procedure was called from
    :type server: MinecraftServer
    :param bot: The bot that the rpc is registered for
    :type bot: LiteBot
    :param data: The data for the handler
    :type data: dict
    """
    def __init__(self, server: MinecraftServer, bot: LiteBot, data: dict):
        super().__init__(server, bot)
        self.data = data
