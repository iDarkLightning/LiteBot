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
        self._repr = []

    @classmethod
    def from_str(cls, str_: str) -> Text:
        instance = Text()
        instance.add_component(text=str_)

        return instance

    @classmethod
    def op_message(cls, str_: str) -> Text:
        instance = Text()
        instance.add_component(text=f"[{str_}]", color=Colors.GRAY, italic=True)

        return instance

    @classmethod
    def bridge_message(cls, src_server_name: str, str_: str) -> Text:
        instance = Text()
        instance.add_component(text=f"[From {src_server_name}] {str_}", color=Colors.GRAY)

        return instance

    def add_line(self):
        self._repr.append(TextComponent(text="\n"))
        return self

    def add_component(self, **kwargs):
        self._repr.append(TextComponent(**kwargs))
        return self

    def build(self):
        return str([i.build() for i in self._repr]).replace("'", "").replace("\\\\", "\\")

class TextComponent:
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k ,v)

    def build(self):
        return json.dumps(self.__dict__)