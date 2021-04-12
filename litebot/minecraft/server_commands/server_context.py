from typing import Optional

from litebot.minecraft.text import Text

WHITE = 16777215

class ServerCommandContext:
    """
    A context object for a ServerCommand.
    Lets us easily interact with both the server and the bot
    through a single object.

    :param server: The server that the command is being executed to
    :type server: MinecraftServer
    :param bot: The bot that the command is registered to
    :type bot: LiteBot
    :param player: The player that executed the command
    :type player: str
    """
    def __init__(self, server, bot, player: str) -> None:
        self.server = server
        self.bot = bot
        self.player = player

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

class ServerEventContext:
    """
    A context object for a ServerCommand.
    Lets us easily interact with both the server and the bot
    through a single object.

    :param server: The server that the command is being executed to
    :type server: MinecraftServer
    :param bot: The bot that the command is registered to
    :type bot: LiteBot
    :param player: An optional player that executed the event
    :type player: str
    """
    def __init__(self, server, bot, player: Optional[str]) -> None:
        self.bot = bot
        self.server = server
        self.player = player