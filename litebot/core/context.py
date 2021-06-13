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

    async def send(self, content=None, *, tts=False, embed=None, file=None,
                                          files=None, delete_after=None, nonce=None,
                                          allowed_mentions=None, reference=None,
                                          mention_author=None, components=None):
        return await super().send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after,
                           nonce=nonce, allowed_mentions=allowed_mentions, reference=reference, mention_author=mention_author,
                           components=components)
