import json
from datetime import datetime

from discord.ext.commands import MemberConverter, MemberNotFound, RoleConverter, RoleNotFound, UserConverter

from litebot.core import SettingTypes, Plugin
from litebot.utils.embeds import InfoEmbed
from plugins.system.settings.utils import pretty_json_code


class SettingEmbed(InfoEmbed):
    def __init__(self, setting):
        self.setting = setting
        super().__init__(setting.name, description=setting.description, timestamp=datetime.utcnow())
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
            try:
                return await RoleConverter().convert(ctx, id)
            except RoleNotFound:
                return await UserConverter().convert(ctx, id)

    def _create_configuration_embed(self):
        embed = InfoEmbed(
            f"Configure {self.setting.name}",
            description="Configure this setting!",
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

class PluginEmbed(InfoEmbed):
    def __init__(self, plugin: Plugin, bot):
        super().__init__(plugin.meta.name, description=plugin.meta.description, timestamp=datetime.utcnow())

        self.plugin = plugin
        self.bot = bot

        self.set_author(name=plugin.meta.id)
        self.set_footer(text=f"Authors: {', '.join(plugin.authors) if plugin.authors else 'Unknown!'}")

        self.configuration_embed = self._create_configuration_embed()

    async def add_usable_by(self, ctx):
        usable_by = [(await self._convert_id(ctx, str(id))).mention for id in self.plugin.id_checks] or ["@everyone"]
        self.add_field(name="Discord Commands Usable By",
                       value=f"Discord commands in this plugin are usable by (this is in addition to ID checks added for each individual setting): {', '.join([i for i in usable_by])}",
                       inline=False)
        self.add_field(name="Minecraft Commands Usable By",
                       value=f"Minecraft commands in this plugin are usable by everyone with OP Level {self.plugin.op_level}, unless otherwise configured for a setting.",
                       inline=False)

    async def _convert_id(self, ctx, id):
        try:
            return await MemberConverter().convert(ctx, id)
        except MemberNotFound:
            try:
                return await RoleConverter().convert(ctx, id)
            except RoleNotFound:
                return await UserConverter().convert(ctx, id)

    def _create_configuration_embed(self):
        embed = InfoEmbed(
            f"Configure {self.plugin.meta.name}",
            description="Configure this plugin!",
            timestamp=datetime.utcnow()
        )

        if self.plugin.config:
            embed.add_field(name="Configuration", value=pretty_json_code(self.plugin.config), inline=False)

        embed.add_field(name="ID Checks", value=pretty_json_code({"id_checks": self.plugin.id_checks}), inline=False)
        embed.add_field(name="OP Level", value=pretty_json_code({"op_level": self.plugin.op_level}), inline=False)

        embed.set_author(name=self.plugin.meta.name)
        embed.set_footer(text=f"Authors: {', '.join(self.plugin.authors) if self.plugin.authors else 'Unknown!'}")

        return embed