from litebot.minecraft.text import Text

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

class ServerEventPayload:
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

    PAYLOAD_MAPPINGS = {
        "on_message": ("message", "player_uuid", "player_name")
    }

    # This is so that we have type hinting for our dynamically set arguments
    message: str
    player_name: str
    player_uuid: str

    def __init__(self, server, bot, event_name, args) -> None:
        self.bot = bot
        self.server = server

        for i, v in enumerate(args):
            setattr(self, ServerEventPayload.PAYLOAD_MAPPINGS[event_name][i], v)

        for attr in ServerEventPayload.PAYLOAD_MAPPINGS[event_name]:
            if not hasattr(self, attr):
                setattr(self, attr, None)

