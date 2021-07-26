class Toggleable:
    """
    A class letting you toggle true or false using a context manager

    Examples:
        using = Toggleable(False)

        with using:
            # `using` will now be True
            perform_action()

        # using is once again False
    """
    def __init__(self, initial: bool = False):
        self._val = initial

    def __enter__(self):
        self._val = not self._val

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._val = not self._val

    def __bool__(self):
        return self._val