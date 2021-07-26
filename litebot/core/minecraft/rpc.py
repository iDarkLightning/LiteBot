from typing import Callable


def rpc(*, name) -> Callable:
    """Decorate a coroutine as an RPC method that can be executed by the server.

    Args:
        name: The name of the RPC method

    Returns:
        A decorator that will mark the coroutine as an RPC method
    """

    def decorator(func) -> Callable:
        func.__rpc_handler__ = True
        func.__name__ = name or func.__name__
        return func

    return decorator