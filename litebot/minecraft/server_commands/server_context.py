from typing import Optional
WHITE = 16777215

class ServerContext:
    """
    A context object for a ServerCommand.
    Lets us easily interact with both the server and the bot
    through a single object.

    :param server: The server that the command is being executed to
    :type server: MinecraftServer
    :param bot: The bot that the command is registered to
    :type bot: LiteBot
    """
    def __init__(self, server, bot, author: str) -> None:
        self.server = server
        self.bot = bot
        self.author = author

    async def send(self, message: str, color: Optional[int] = None) -> None:
        """
        Enables us to easily send messages to the server
        from our command
        :param message: The message to send
        :type message: str
        :param color: The color of our message in game
        :type color: Optional[int]
        """
        await self.server.send_system_message(
            {"player": self.author}, {"message": message, "color": color if color else WHITE})