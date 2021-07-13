from discord import Embed

RED = 0xFF0000
GREEN = 0x32CD32
YELLOW = 0xFFA500
INFO_COLOR = 0x9696FA

class ErrorEmbed(Embed):
    """
    An _embed preset for errors
    """
    def __init__(self, msg: str, traceback = None, **kwargs) -> None:
        super().__init__(title=msg, color=RED, **kwargs)

class WarningEmbed(Embed):
    """
    An _embed preset for warnings
    """
    def __init__(self, msg: str, **kwargs) -> None:
        super().__init__(title=msg, color=YELLOW, **kwargs)

class SuccessEmbed(Embed):
    """
    An _embed preset for success messages
    """
    def __init__(self, msg: str, **kwargs) -> None:
        super().__init__(title=msg, color=GREEN, **kwargs)

class InfoEmbed(Embed):
    """
    An _embed preset for information
    """
    def __init__(self, msg: str, **kwargs) -> None:
        super().__init__(title=msg, color=INFO_COLOR, **kwargs)