

def rpc(**kwargs):
    def decorator(func):
        func.__rpc_handler__ = True
        func.__name__ = kwargs.get("name", func.__name__)
        return func

    return decorator