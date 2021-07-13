from discord.ext import commands


class LiteBotException(Exception):
    """Base exception class for litebot

    All exceptions that originate from this package
    can be caught through this error
    """
    pass

class InvalidEvent(Exception):
    """
    Exception produced when trying to dispatch an invalid event
    """
    pass


class AuthFailure(LiteBotException):
    """
    Exception produced when a server tries to connect with an invalid auth token
    """
    pass


class ArgumentError(LiteBotException):
    """
    Exception produced when the argument type for a server command does not inherit ArgumentType
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


class ServerNotRunningCarpet(MinecraftServerException):
    """
    Exception produced when methods requiring carpet mod are performed
    with a server that does not have the mod installed
    """
    pass


class BaseCommandError(LiteBotException, commands.errors.CommandError):
    """
    Base exception for custom command errors
    raised by LiteBot
    """
    pass


class TicketNotFound(BaseCommandError):
    """
    Exception produced when a ticket command is run in a non-ticket channel
    """
    pass
