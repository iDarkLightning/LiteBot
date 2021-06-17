import os
from datetime import datetime

from discord import Member

from litebot.utils.embeds import SuccessEmbed, InfoEmbed


class BackupCreatedEmbed(SuccessEmbed):
    def __init__(self, server, name: str, path: str, creator: Member, **kwargs):
        super().__init__("Backup Created Successfully!", timestamp=datetime.utcnow(), **kwargs)

        size = round(os.path.getsize(path) / (1 * pow(10, 9)), 2)

        self.set_author(name=server.name.upper())
        self.add_field(name="Name", value=name)
        self.add_field(name="Size", value=f"{size}GB")

        self.set_footer(text=f"Created By: {creator.display_name}", icon_url=creator.avatar_url)

class BackupRestoredEmbed(SuccessEmbed):
    def __init__(self, server, restorer: Member, **kwargs):
        super().__init__("Backup Restored Successfully!", timestamp=datetime.utcnow(), **kwargs)

        self.set_author(name=server.name.upper())
        self.set_footer(text=f"Created By: {restorer.display_name}", icon_url=restorer.avatar_url)

class BackupDownloadEmbed(InfoEmbed):
    def __init__(self, server, name: str, url: str, **kwargs):
        super().__init__("Download Backup!", timestamp=datetime.utcnow(),
                         description=f"[Click to Download]({url})",**kwargs)

        self.set_author(name=server.name.upper())
        self.add_field(name="Name", value=name)
        self.set_footer(text="This link will expire in 5 minutes!")