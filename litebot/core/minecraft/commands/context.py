from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from litebot.core.minecraft import Player
from litebot.core.minecraft.text import Text

if TYPE_CHECKING:
    from litebot.core.minecraft.commands.action import ServerCommand
    from litebot.litebot import LiteBot
    from litebot.core.minecraft import MinecraftServer

class ServerCommandContext:
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
        self.command = command
        self.cog = command.cog
        self.server = server
        self.bot = bot
        self.after_invoke_args = {}
        self.args = kwargs["args"]
        self.full_args = kwargs["full_args"]
        self.player = Player(**json.loads(player_data))

    def __setitem__(self, key, value):
        self.after_invoke_args[key] = value

    async def invoke(self):
        args = [self.command.arg_types[name](arg).val for name, arg in self.args.items()]

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

class ServerEventPayload:
    """
    The payload for a server event.
    Lets us access all the data for our event, as well as access the server and bot objects.

    :param server: The server that the command is being executed to
    :type server: MinecraftServer
    :param bot: The bot that the command is registered to
    :type bot: LiteBot
    :param event_name: The name of the event being registered
    :type event_name: Str
    :param args: The arguments for the event
    :type args: list[Any]
    """

    PAYLOAD_MAPPINGS = {
        "on_message": ("message", "player_uuid", "player_name")
    }

    # This is so that we have type hinting for our dynamically set arguments
    message: str
    player_name: str
    player_uuid: str

    def __init__(self, server: MinecraftServer, bot: LiteBot, event_name: str, args: list[Any]) -> None:
        self.bot = bot
        self.server = server

        for i, v in enumerate(args):
            setattr(self, ServerEventPayload.PAYLOAD_MAPPINGS[event_name][i], v)

        for attr in ServerEventPayload.PAYLOAD_MAPPINGS[event_name]:
            if not hasattr(self, attr):
                setattr(self, attr, None)

