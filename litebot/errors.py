class LiteBotException(Exception):
    """Base exception class for litebot

    All exceptions that originate from this package
    can be caught through this error
    """
    pass

class ConfigError(LiteBotException):
    """
    Base exception for all errors related to the config
    """
    pass

class MinecraftServerException(LiteBotException):
    """
    Base exception for all errors related to the Minecraft server
    """
    pass

class RconException(MinecraftServerException):
    """
    Exception for errors regarding the rcon module
    """
    pass

class ServerConnectionFailed(MinecraftServerException):
    """
    Exception produced when a connection to  a minecraft server
    failed
    """
    pass

class ServerNotFound(MinecraftServerException):
    """
    Exception produced when there is no MinecraftServer
    with given information
    """
    pass