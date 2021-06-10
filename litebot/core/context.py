from typing import Optional

from discord.ext.commands import Context as DPYContext

from litebot.core import Setting


class Context(DPYContext):
    @property
    def setting(self) -> Optional[Setting]:
        if self.command is None:
            return None

        try:
            return self.command.callback.__setting__
        except AttributeError:
            return self.command.root_parent.callback.__setting__

    @property
    def config(self) -> Optional[dict]:
        if self.setting is None:
            return None
        return self.setting.config
