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

class ConfigFirstGenerated(ConfigError):
    """
    Exception that is thrown when a new blank config has just been
    generated
    """
    pass

class NewConfigFields(ConfigError):
    """
    Exception that is generated when new fields have been added to
    the config
    """
    pass
