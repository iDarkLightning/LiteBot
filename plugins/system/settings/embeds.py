import json
from datetime import datetime

from discord.ext.commands import MemberConverter, MemberNotFound, RoleConverter, RoleNotFound, UserConverter

from litebot.core import SettingTypes
from litebot.utils.embeds import InfoEmbed
from plugins.system.settings.utils import pretty_json_code


class SettingEmbed(InfoEmbed):
    def __init__(self, setting):
        self.setting = setting
        description = setting.description + "⠀" * (50 - len(setting.description)) if len(setting.description) <= 50 else setting.description
        super().__init__(setting.name, description=description, timestamp=datetime.utcnow())
        self.add_field(name="Enabled", value=setting.enabled, inline=False)

        if setting.config:
            self.add_field(name="Configuration", value=pretty_json_code(self.setting.config), inline=False)

        self.set_author(name=setting.plugin.meta.name)
        self.set_footer(text=f"Authors: {', '.join(setting.plugin.authors) if setting.plugin.authors else 'Unknown!'}")

        self.configuration_embed = self._create_configuration_embed()

    async def add_usable_by(self, ctx):
        if self.setting.type == SettingTypes.DISC_COMMAND:
            usable_by = [(await self._convert_id(ctx, str(id))).mention for id in self.setting.id_checks] or ["@everyone"]
            self.add_field(name="Usable By", value=f"This command is usable by: {', '.join([i for i in usable_by])}")
        elif self.setting.type == SettingTypes.MC_COMMAND:
            self.add_field(name="Usable By", value=f"This command is usable by everyone with OP Level: {self.setting.op_level}")

    async def _convert_id(self, ctx, id):
        try:
            return await MemberConverter().convert(ctx, id)
        except MemberNotFound:
            return await RoleConverter().convert(ctx, id)
        except RoleNotFound:
            return await UserConverter().convert(ctx, id)

    def _create_configuration_embed(self):
        embed = InfoEmbed(
            f"Configure {self.setting.name}",
            description="Configure this _setting!",
            timestamp=datetime.utcnow()
        )

        if self.setting.config:
            embed.add_field(name="Configuration", value=pretty_json_code(self.setting.config), inline=False)

        if self.setting.type == SettingTypes.DISC_COMMAND:
            embed.add_field(name="ID Checks", value=pretty_json_code({"id_checks": self.setting.id_checks}), inline=False)
        elif self.setting.type == SettingTypes.MC_COMMAND:
            embed.add_field(name="OP Level", value=pretty_json_code({"op_level": self.setting.op_level}), inline=False)

        embed.set_author(name=self.setting.plugin.meta.name)
        embed.set_footer(text=f"Authors: {', '.join(self.setting.plugin.authors) if self.setting.plugin.authors else 'Unknown!'}")

        return embed