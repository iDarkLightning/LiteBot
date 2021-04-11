from discord.ext import commands

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

class ServerNotRunningLTA(MinecraftServerException):
    """
    Exception produced when methods requiring LTA are performed
    with a server that does not have the mod installed
    """
    pass

class ServerNotRunningCarpet(MinecraftServerException):
    """
    Exception produced when methods requiring carpet mod are performed
    with a server that does not have the mod installed
    """
    pass

class ServerActionNotFound(MinecraftServerException):
    """
    Exception produced when trying to run a command
    from the server, that does not exist
    """
    pass

class BaseCommandError(LiteBotException, commands.errors.CommandError):
    """
    Base exception for custom command errors
    raised by LiteBot
    """
    pass

class ConfirmationDenied(BaseCommandError):
    """
    Exception produced when user denies confirmation
    """
    pass

class PollCommandError(BaseCommandError):
    """
    Exception produced when an error occurs with the poll command
    """
    pass

class ChannelNotWhitelisted(BaseCommandError):
    """
    Exception produced when a command which is whitelisted is performed on a unwhitelisted channel.
    """