from litebot.utils.string_utils import split_string
from litebot.utils.embeds import InfoEmbed
from litebot.utils.markdown import CODE_BLOCK


class PanelEmbed(InfoEmbed):
    def __init__(self, author, logs, server):
        super().__init__("Server Panel",
                         description=CODE_BLOCK.format("", "\n".join(split_string("\n".join(logs[::-1]), 1980)[0].split("\n")[::-1])))
        self.server = server

        self.set_author(name=server.name.upper())

        self.set_footer(text=author.display_name, icon_url=author.avatar_url)