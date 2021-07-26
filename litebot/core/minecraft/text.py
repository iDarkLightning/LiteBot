from __future__ import annotations
import json

class Colors:
    BLACK = "#000000"
    DARK_BLUE = "#0000AA"
    DARK_GREEN = "#00AA00"
    DARK_AQUA = "#00AAAA"
    DARK_RED = "#AA0000"
    DARK_PURPLE = "#AA00AA"
    GOLD = "#FFAA00"
    GRAY = "#AAAAAA"
    DARK_GRAY = "#555555"
    BLUE = "#5555FF"
    GREEN = "#55FF55"
    AQUA = "#55FFFF"
    RED = "#FF5555"
    LIGHT_PURPLE = "#FF5555"
    YELLOW = "#FFFF55"
    WHITE = "#FFFFFF"

class Text:
    def __init__(self):
        """
        A builder to build complex text objects to send messages to the server.
        """
        self._repr = []

    @classmethod
    def from_str(cls, str_: str) -> Text:
        """
        Create a text object from a string

        Args:
            str_: The string to create the text object from

        Returns:
            The text object
        """

        instance = Text()
        instance.add_component(text=str_)

        return instance

    @classmethod
    def op_message(cls, str_: str) -> Text:
        """
        Create a text object that mimics the style for OP messages in-game

        Args:
            str_: The message to style

        Returns:
            The text object
        """

        instance = Text()
        instance.add_component(text=f"[{str_}]", color=Colors.GRAY, italic=True)

        return instance

    @classmethod
    def error_message(cls, str_: str) -> Text:
        """
        Create a text object that mimics the style for error messages in-game

        Args:
            str_: The message to style

        Returns:
            The text object
        """

        return Text().add_component(text=str_, color=Colors.RED)

    def add_line(self):
        """Add a new line to the text object
        """

        self._repr.append(_TextComponent(text="\n"))
        return self

    def add_component(self, **kwargs):
        """Add a new component to the builder

        Args:
            **kwargs: The kwargs to build the component with

        Returns:
            The current builder
        """

        self._repr.append(_TextComponent(**kwargs))
        return self

    def build(self):
        """
        Returns:
            The JSON string to send to the server
        """
        return str([i.build() for i in self._repr]).replace("'", "").replace("\\\\", "\\")

class _TextComponent:
    def __init__(self, **kwargs):
        """
        A component object to use with the Text builder.

        This is not meant to be instantiated directly, and should be used
        via the provided functional interfaces in the Text builder.

        Args:
            **kwargs: The kwargs to build the component with
        """
        for k,v in kwargs.items():
            setattr(self, k ,v)

    def build(self) -> str:
        """
        Returns:
            The JSON string representing this component
        """
        return json.dumps(self.__dict__)