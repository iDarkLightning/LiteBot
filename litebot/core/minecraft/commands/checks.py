from typing import Callable

from litebot.core import ServerCommand


def check(predicate: Callable) -> Callable:
    """A decorator to add a check to a server command

    Args:
        predicate: The check that should be run

    Returns:
        A decorator function that will add the check to the command
    """

    def decorator(cmd: ServerCommand):
        if not isinstance(cmd, ServerCommand):
            raise TypeError("Checks can only be applied to server commands!")

        cmd.checks.append(predicate)
        return cmd

    return decorator

def requires(predicate: Callable) -> Callable:
    """A decorator to add a requirement to a server command.

    This is different from a check since a check is validated on runtime
    whereas this is run when the command tree is sent.

    Args:
        predicate: The requirement that should be run

    Returns:
        A decorator function that will add the requirement to the command
    """

    def decorator(cmd: ServerCommand):
        if not isinstance(cmd, ServerCommand):
            raise TypeError("Requirements can only be applied to server commands!")

        cmd.requirements.append(predicate)
        return cmd

    return decorator