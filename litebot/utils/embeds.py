from datetime import datetime

from discord import Embed

from litebot.utils.enums import ModeratorActions

RED = 0xFF0000
GREEN = 0x32CD32
YELLOW = 0xFFA500
INFO_COLOR = 0x9696FA

class ErrorEmbed(Embed):
    """
    An embed preset for errors
    """
    def __init__(self, msg: str, traceback = None, **kwargs) -> None:
        super().__init__(title=msg, color=RED, **kwargs)

class WarningEmbed(Embed):
    """
    An embed preset for warnings
    """
    def __init__(self, msg: str, **kwargs) -> None:
        super().__init__(title=msg, color=YELLOW, **kwargs)

class SuccessEmbed(Embed):
    """
    An embed preset for success messages
    """
    def __init__(self, msg: str, **kwargs) -> None:
        super().__init__(title=msg, color=GREEN, **kwargs)

class InfoEmbed(Embed):
    """
    An embed preset for information
    """
    def __init__(self, msg: str, **kwargs) -> None:
        super().__init__(title=msg, color=INFO_COLOR, **kwargs)

class ModeratorLogEmbed(InfoEmbed):
    """
    An embed preset for moderator actions
    """
    def __init__(self, action: ModeratorActions, reason, executer, victim, **kwargs):
        if action == ModeratorActions.KICK:
            super().__init__("A user was kicked!", timestamp=datetime.utcnow(), **kwargs)
            self.description = f"Kick Info: {reason}"
        elif action == ModeratorActions.BAN:
            super().__init__("A user was banned!", timestamp=datetime.utcnow(), **kwargs)
            self.description = f"Ban Info: {reason}"
        elif action == ModeratorActions.MUTE:
            super().__init__("A user was muted!", timestamp=datetime.utcnow(), **kwargs)
            self.description = f"Mute Info: {reason}"
        elif action == ModeratorActions.PARDON:
            super().__init__("A user was pardoned", timestamp=datetime.utcnow(), **kwargs)
            self.description = f"Pardon Info: {reason}"

        self.add_field(name="Executor", value=f"{executer}: {executer.id}")
        self.add_field(name="Victim", value=f"{victim}: {victim.id}", inline=False)
        self.set_thumbnail(url=victim.avatar_url)