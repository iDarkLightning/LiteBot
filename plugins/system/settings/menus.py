import copy
import json

from discord import HTTPException
from discord.ext.commands import UserNotFound

from discord_components import Button, ButtonStyle, InteractionType

from litebot.core import SettingTypes
from litebot.core.components import Interaction
from litebot.core.context import Context
from litebot.modules.system.converters import JSONConverter
from litebot.utils.data_manip import flatten_dict, unflatten_dict
from litebot.utils.fmt_strings import CODE_BLOCK
from plugins.system.settings.utils import Timer
from plugins.system.settings.embeds import SettingEmbed, PluginEmbed


class SettingsMenu:
    class InteractionTypes:
        BACK = "back"
        ENABLE = "enable"
        DISABLE = "disable"
        CONFIGURE = "configure"
        NEXT = "next"

    def __init__(self, ctx: Context, embeds: list[SettingEmbed], timeout=120):
        self._ctx = ctx
        self._embeds = embeds
        self._idx = 0
        self._cur = embeds[self._idx]
        self._message = None
        self._timeout = timeout
        self._timer = None
        self._buttons = [
                        Button(style=ButtonStyle.gray, label="⬆ Back", id=SettingsMenu.InteractionTypes.BACK),
                        Button(style=ButtonStyle.green, label="Enable", id=SettingsMenu.InteractionTypes.ENABLE),
                        Button(style=ButtonStyle.red, label="Disable", id=SettingsMenu.InteractionTypes.DISABLE),
                        Button(style=ButtonStyle.gray, label="⬇ Next", id=SettingsMenu.InteractionTypes.NEXT),
        ]

        self.__task = None

    async def start(self):
        """
        Start the menu
        """
        components = self._get_buttons()
        self._message = await self._ctx.send(embed=self._cur, components=[components])
        self.__task = self._ctx.bot.loop.create_task(self._loop())

        self._timer = Timer(self._done, self._timeout)
        await self._timer.start()

    async def _loop(self):
        while True:
            def check(m):
                return m.id == self._message.id and self._message.id and m.channel == self._ctx.channel and m.author == self._ctx.author

            interaction = await self._ctx.bot.wait_for("button_click", check=check)
            await interaction.respond(type=InteractionType.DeferredUpdateMessage)
            await self._timer.reset()

            interaction_type = interaction.raw_data["d"]["data"]["custom_id"]
            await getattr(self, f"_{interaction_type}", lambda i: None)()

    async def _enable(self):
        if self._cur.setting.enabled:
            return

        self._cur.setting.enabled = True
        self._ctx.bot.settings_manager.update_setting(self._cur.setting)

        self._cur.setting.cog.reload(self._ctx.bot)
        components = self._get_buttons()

        self._cur.set_field_at(0, name="Enabled", value="True", inline=False)

        for server in self._ctx.bot.servers:
            await server.send_command_tree()

        await self._message.edit(embed=self._cur, components=[components])

    async def _disable(self):
        if not self._cur.setting.enabled:
            return

        self._cur.setting.enabled = False
        self._ctx.bot.settings_manager.update_setting(self._cur.setting)

        self._cur.setting.cog.reload(self._ctx.bot)
        components = self._get_buttons()

        self._cur.set_field_at(0, name="Enabled", value="False", inline=False)

        for server in self._ctx.bot.servers:
            await server.send_command_tree()

        await self._message.edit(embed=self._cur, components=[components])

    async def _next(self):
        self._idx += 1
        self._cur = self._embeds[self._idx]
        self._ctx.bot.processing_plugin = self._cur.setting.plugin
        components = self._get_buttons()

        await self._message.edit(embed=self._cur, components=[components])

    async def _back(self):
        self._idx -= 1
        self._cur = self._embeds[self._idx]
        components = self._get_buttons()
        self._ctx.bot.processing_plugin = self._cur.setting.plugin

        await self._message.edit(embed=self._cur, components=[components])

    async def _configure(self):
        config_menu = SettingsConfigMenu(self._ctx, self._message, self._cur, self._timer)
        task = self._ctx.bot.loop.create_task(config_menu.start())
        await task

        self._cur = SettingEmbed(self._cur.setting)
        await self._cur.add_usable_by(self._ctx)
        self._embeds[self._idx] = self._cur

        await self._message.edit(embed=self._cur, components=[self._get_buttons()])

    def _get_buttons(self):
        components = copy.copy(self._buttons)
        if self._cur.setting.type in (SettingTypes.DISC_COMMAND, SettingTypes.MC_COMMAND) or self._cur.setting.config:
            components.insert(3, Button(style=ButtonStyle.blue, label="Configure", id=SettingsMenu.InteractionTypes.CONFIGURE))

        if self._idx == 0:
            components.pop(0)

        if self._idx == len(self._embeds) - 1:
            components.pop()

        return components

    async def _done(self):
        self.__task.cancel()

        self._cur = SettingEmbed(self._cur.setting)
        await self._cur.add_usable_by(self._ctx)
        self._embeds[self._idx] = self._cur

        components = self._get_buttons()
        for c in components:
            c.disabled = True

        await self._message.edit(embed=self._cur, components=[components])


class SettingsConfigMenu:
    class InteractionTypes:
        BACK = "back"
        ADD_ID_CHECK = "add_id_check"
        REMOVE_ID_CHECK = "remove_id_check"
        CHANGE_OP_LEVEL = "change_op_level"
        CONFIGURE = "configure"

    def __init__(self, ctx, msg, embed: SettingEmbed, timer):
        self._ctx = ctx
        self._message = msg
        self._embed = embed.configuration_embed
        self._setting = embed.setting
        self._timer = timer
        self._components = [
            Button(style=ButtonStyle.gray, label="Back", id=SettingsMenu.InteractionTypes.BACK)
        ]

        if self._setting.type == SettingTypes.DISC_COMMAND:
            self._components.append(Button(style=ButtonStyle.green, label="Add ID Check", id=SettingsConfigMenu.InteractionTypes.ADD_ID_CHECK))
            self._components.append(Button(style=ButtonStyle.red, label="Remove ID Check", id=SettingsConfigMenu.InteractionTypes.REMOVE_ID_CHECK))
        elif self._setting.type == SettingTypes.MC_COMMAND:
            self._components.append(Button(style=ButtonStyle.green, label="Change OP Level", id=SettingsConfigMenu.InteractionTypes.CHANGE_OP_LEVEL))

        if self._setting.config:
            self._components.append(Button(style=ButtonStyle.blue, label="Configure", id=SettingsConfigMenu.InteractionTypes.CONFIGURE))

    async def start(self):
        """
        Start the menu
        """
        await self._message.edit(embed=self._embed, components=[self._components])

        while True:
            def check(m):
                return m.channel == self._ctx.channel and m.author == self._ctx.author

            interaction = await self._ctx.bot.wait_for("button_click", check=check)
            await self._timer.reset()
            interaction_type = interaction.raw_data["d"]["data"]["custom_id"]
            if interaction_type == SettingsConfigMenu.InteractionTypes.BACK:
                await interaction.respond(type=InteractionType.DeferredUpdateMessage)
                break

            with self._timer:
                await getattr(self, f"_{interaction_type}", lambda i: None)(interaction)

    async def _add_id_check(self, interaction: Interaction):
        await interaction.respond(content="Enter the Role/Member ID you would like to add: ")

        def check(m):
            return m.channel == self._ctx.channel and m.author == self._ctx.author

        msg = await self._ctx.bot.wait_for("message", check=check)
        await msg.delete()

        try:
            userorrole = await self._ctx.bot.fetch_user(msg.content)
        except (UserNotFound, HTTPException):
            try:
                userorrole = [i for i in await self._ctx.guild.fetch_roles() if i.id == msg.content][0]
            except IndexError:
                return await interaction.edit(content=f"`{msg.content}` is not a valid ID!")

        if userorrole.id in self._setting.id_checks:
            return await interaction.edit(content=f"{userorrole.mention} is already a valid user!")

        self._setting.id_checks.append(userorrole.id)
        self._ctx.bot.settings_manager.update_setting(self._setting)

        idx = 0 if not self._setting.config else 1
        self._embed.set_field_at(idx, name="ID Checks", value=CODE_BLOCK.format("json",
                                                                                json.dumps({"id_checks": self._setting.id_checks},
                                                                                           indent=4)), inline=False)
        await self._message.edit(embed=self._embed, components=[self._components])
        return await interaction.edit(content=f"{userorrole.mention} has been added to the list of valid users!")

    async def _remove_id_check(self, interaction):
        await interaction.respond(content="Enter the Role/Member ID you would like to remove: ")

        def check(m):
            return m.channel == self._ctx.channel and m.author == self._ctx.author

        msg = await self._ctx.bot.wait_for("message", check=check)
        await msg.delete()

        if msg.content.isnumeric() and int(msg.content) not in self._setting.id_checks:
            return await interaction.respond(content=f"`{msg.content}` is not in the current list of valid users!")
        elif not msg.content.isnumeric():
            return await interaction.respond(content=f"`{msg.content}` is not a valid ID!")

        id = self._setting.id_checks.pop(self._setting.id_checks.index(int(msg.content)))
        self._ctx.bot.settings_manager.update_setting(self._setting)

        idx = 0 if not self._setting.config else 1

        self._embed.set_field_at(idx, name="ID Checks", value=CODE_BLOCK.format("json",
                                                                                json.dumps({"id_checks": self._setting.id_checks},
                                                                                           indent=4)), inline=False)
        await self._message.edit(embed=self._embed, components=[self._components])
        return await interaction.edit(content=f"{id} has been removed from the list of valid users!")

    async def _change_op_level(self, interaction: Interaction):
        await interaction.respond(content="What would you like to change the OP Level to? ")

        def check(m):
            return m.channel == self._ctx.channel and m.author == self._ctx.author

        msg = await self._ctx.bot.wait_for("message", check=check)
        await msg.delete()

        if not msg.content.isnumeric() or not (0 <= int(msg.content) <= 4):
            return await interaction.edit(content=f"{msg.content} is not a valid OP Level!")
        self._setting.op_level = int(msg.content)
        self._ctx.bot.settings_manager.update_setting(self._setting)

        idx = 0 if not self._setting.config else 1
        self._embed.set_field_at(idx, name="OP Level", value=CODE_BLOCK.format("json",
                                                                               json.dumps(
                                                                                 {"op_level": self._setting.op_level},
                                                                                 indent=4)), inline=False)
        await self._message.edit(embed=self._embed, components=[self._components])
        return await interaction.edit(content=f"OP Level has been changed to `{self._setting.op_level}`")

    async def _configure(self, interaction):
        flattened_dict = flatten_dict(self._setting.config)
        await interaction.respond(content="Please enter the key that you would like to change, using `.` to traverse levels: ")

        def check(m):
            return m.channel == self._ctx.channel and m.author == self._ctx.author

        msg = await self._ctx.bot.wait_for("message", check=check)
        await msg.delete()

        if msg.content not in flattened_dict:
            return await interaction.edit(content=f"`{msg.content}` is not a valid key!")

        key = msg.content

        await interaction.edit(content=f"Please enter the value you would like to change `{key}` to!")

        msg = await self._ctx.bot.wait_for("message", check=check)
        await msg.delete()

        value = await JSONConverter().convert(self._ctx, msg.content)
        if type(value) is not type(flattened_dict[key]):
            return await interaction.edit(content=f"`{value}` is not the appropriate type for `{key}`")

        flattened_dict[key] = value
        self._setting.config.update(unflatten_dict(flattened_dict))
        self._ctx.bot.settings_manager.update_setting(self._setting)

        self._embed.set_field_at(0, name="Configuration", value=CODE_BLOCK.format("json",
                                                                                  json.dumps(
                                                                                 self._setting.config,
                                                                                 indent=4)), inline=False)
        await self._message.edit(embed=self._embed, components=[self._components])
        return await interaction.edit(content=f"The config value for `{key}` has been updated to `{value}`")

class PluginsConfigMenu:
    class InteractionTypes:
        BACK = "back"
        ADD_ID_CHECK = "add_id_check"
        REMOVE_ID_CHECK = "remove_id_check"
        CHANGE_OP_LEVEL = "change_op_level"
        CONFIGURE = "configure"

    def __init__(self, ctx, msg, embed: PluginEmbed, timer):
        self._ctx = ctx
        self._message = msg
        self._embed = embed.configuration_embed
        self._plugin = embed.plugin
        self._timer = timer
        self._components = [
            Button(style=ButtonStyle.gray, label="Back", id=SettingsMenu.InteractionTypes.BACK),
            Button(style=ButtonStyle.green, label="Add ID Check", id=SettingsConfigMenu.InteractionTypes.ADD_ID_CHECK),
            Button(style=ButtonStyle.red, label="Remove ID Check", id=SettingsConfigMenu.InteractionTypes.REMOVE_ID_CHECK),
            Button(style=ButtonStyle.green, label="Change OP Level", id=SettingsConfigMenu.InteractionTypes.CHANGE_OP_LEVEL),
        ]

        if self._plugin.config:
            self._components.append(Button(style=ButtonStyle.blue, label="Configure", id=SettingsConfigMenu.InteractionTypes.CONFIGURE))

    async def start(self):
        """
        Start the menu
        """
        await self._message.edit(embed=self._embed, components=[self._components])

        while True:
            def check(m):
                return m.channel == self._ctx.channel and m.author == self._ctx.author and m.id == self._message.id

            interaction = await self._ctx.bot.wait_for("button_click", check=check)
            await self._timer.reset()
            interaction_type = interaction.raw_data["d"]["data"]["custom_id"]
            if interaction_type == PluginsConfigMenu.InteractionTypes.BACK:
                await interaction.respond(type=InteractionType.DeferredUpdateMessage)
                break

            with self._timer:
                await getattr(self, f"_{interaction_type}", lambda i: None)(interaction)

    async def _add_id_check(self, interaction: Interaction):
        await interaction.respond(content="Enter the Role/Member ID you would like to add: ")

        def check(m):
            return m.channel == self._ctx.channel and m.author == self._ctx.author

        msg = await self._ctx.bot.wait_for("message", check=check)
        await msg.delete()

        try:
            userorrole = await self._ctx.bot.fetch_user(msg.content)
        except (UserNotFound, HTTPException):
            try:
                userorrole = [i for i in await self._ctx.guild.fetch_roles() if i.id == msg.content][0]
            except IndexError:
                return await interaction.edit(content=f"`{msg.content}` is not a valid ID!")

        if userorrole.id in self._plugin.id_checks:
            return await interaction.edit(content=f"{userorrole.mention} is already a valid user!")

        self._plugin.id_checks.append(userorrole.id)
        self._ctx.bot.settings_manager.update_plugin(self._plugin)

        idx = 0 if not self._plugin.config else 1
        self._embed.set_field_at(idx, name="ID Checks", value=CODE_BLOCK.format("json",
                                                                                json.dumps({"id_checks": self._plugin.id_checks},
                                                                                           indent=4)), inline=False)
        await self._message.edit(embed=self._embed, components=[self._components])
        return await interaction.edit(content=f"{userorrole.mention} has been added to the list of valid users!")

    async def _remove_id_check(self, interaction):
        await interaction.respond(content="Enter the Role/Member ID you would like to remove: ")

        def check(m):
            return m.channel == self._ctx.channel and m.author == self._ctx.author

        msg = await self._ctx.bot.wait_for("message", check=check)
        await msg.delete()

        if msg.content.isnumeric() and int(msg.content) not in self._plugin.id_checks:
            return await interaction.respond(content=f"`{msg.content}` is not in the current list of valid users!")
        elif not msg.content.isnumeric():
            return await interaction.respond(content=f"`{msg.content}` is not a valid ID!")

        id = self._plugin.id_checks.pop(self._plugin.id_checks.index(int(msg.content)))
        self._ctx.bot.settings_manager.update_plugin(self._plugin)

        for setting in self._ctx.bot.settings_manager.settings.values():
            if setting.plugin is self._plugin:
                setting.id_checks.pop(setting.id_checks.index(int(msg.content)))

        idx = 0 if not self._plugin.config else 1

        self._embed.set_field_at(idx, name="ID Checks", value=CODE_BLOCK.format("json",
                                                                                json.dumps({"id_checks": self._plugin.id_checks},
                                                                                           indent=4)), inline=False)
        await self._message.edit(embed=self._embed, components=[self._components])
        return await interaction.edit(content=f"{id} has been removed from the list of valid users!")

    async def _change_op_level(self, interaction: Interaction):
        await interaction.respond(content="What would you like to change the OP Level to? ")

        def check(m):
            return m.channel == self._ctx.channel and m.author == self._ctx.author

        msg = await self._ctx.bot.wait_for("message", check=check)
        await msg.delete()

        if not msg.content.isnumeric() or not (0 <= int(msg.content) <= 4):
            return await interaction.edit(content=f"{msg.content} is not a valid OP Level!")
        self._plugin.op_level = int(msg.content)
        self._ctx.bot.settings_manager.update_plugin(self._plugin)

        idx = 1 if not self._plugin.config else 2
        self._embed.set_field_at(idx, name="OP Level", value=CODE_BLOCK.format("json",
                                                                               json.dumps(
                                                                                 {"op_level": self._plugin.op_level},
                                                                                 indent=4)), inline=False)
        await self._message.edit(embed=self._embed, components=[self._components])
        return await interaction.edit(content=f"OP Level has been changed to `{self._plugin.op_level}`")

    async def _configure(self, interaction):
        flattened_dict = flatten_dict(self._plugin.config)
        await interaction.respond(content="Please enter the key that you would like to change, using `.` to traverse levels: ")

        def check(m):
            return m.channel == self._ctx.channel and m.author == self._ctx.author

        msg = await self._ctx.bot.wait_for("message", check=check)
        await msg.delete()

        if msg.content not in flattened_dict:
            return await interaction.edit(content=f"`{msg.content}` is not a valid key!")

        key = msg.content

        await interaction.edit(content=f"Please enter the value you would like to change `{key}` to!")

        msg = await self._ctx.bot.wait_for("message", check=check)
        await msg.delete()

        value = await JSONConverter().convert(self._ctx, msg.content)
        if type(value) is not type(flattened_dict[key]):
            return await interaction.edit(content=f"`{value}` is not the appropriate type for `{key}`")

        flattened_dict[key] = value
        self._plugin.config.update(unflatten_dict(flattened_dict))
        self._ctx.bot.settings_manager.update_setting(self._plugin)

        self._embed.set_field_at(0, name="Configuration", value=CODE_BLOCK.format("json",
                                                                                  json.dumps(
                                                                                 self._plugin.config,
                                                                                 indent=4)), inline=False)
        await self._message.edit(embed=self._embed, components=[self._components])
        return await interaction.edit(content=f"The config value for `{key}` has been updated to `{value}`")


class PluginsMenu:
    class InteractionTypes:
        BACK = "back"
        CONFIGURE = "configure"
        NEXT = "next"

    def __init__(self, ctx: Context, embeds: list[PluginEmbed], timeout=120):
        self._ctx = ctx
        self._embeds = embeds
        self._idx = 0
        self._cur = embeds[self._idx]
        self._message = None
        self._timeout = timeout
        self._timer = None
        self._buttons = [
            Button(style=ButtonStyle.gray, label="⬆ Back", id=PluginsMenu.InteractionTypes.BACK),
            Button(style=ButtonStyle.blue, label="Configure", id=PluginsMenu.InteractionTypes.CONFIGURE),
            Button(style=ButtonStyle.gray, label="⬇ Next", id=PluginsMenu.InteractionTypes.NEXT)
        ]

        self.__task = None

    async def start(self):
        components = self._get_buttons()
        self._message = await self._ctx.send(embed=self._cur, components=[components])
        self.__task = self._ctx.bot.loop.create_task(self._loop())

        self._timer = Timer(self._done, self._timeout)
        await self._timer.start()

    async def _loop(self):
        while True:
            def check(m):
                return m.channel == self._ctx.channel and m.author == self._ctx.author and m.id == self._message.id

            interaction = await self._ctx.bot.wait_for("button_click", check=check)
            await interaction.respond(type=InteractionType.DeferredUpdateMessage)
            await self._timer.reset()

            interaction_type = interaction.raw_data["d"]["data"]["custom_id"]
            await getattr(self, f"_{interaction_type}", lambda i: None)()

    async def _next(self):
        self._idx += 1
        self._cur = self._embeds[self._idx]
        self._ctx.bot.processing_plugin = self._cur.plugin
        components = self._get_buttons()

        await self._message.edit(embed=self._cur, components=[components])

    async def _back(self):
        self._idx -= 1
        self._cur = self._embeds[self._idx]
        components = self._get_buttons()
        self._ctx.bot.processing_plugin = self._cur.plugin

        await self._message.edit(embed=self._cur, components=[components])

    async def _configure(self):
        config_menu = PluginsConfigMenu(self._ctx, self._message, self._cur, self._timer)
        task = self._ctx.bot.loop.create_task(config_menu.start())
        await task

        self._cur = PluginEmbed(self._cur.plugin, self._ctx.bot)
        await self._cur.add_usable_by(self._ctx)
        self._embeds[self._idx] = self._cur

        await self._message.edit(embed=self._cur, components=[self._get_buttons()])

    async def _done(self):
        self.__task.cancel()

        self._cur = PluginEmbed(self._cur.plugin, self._ctx.bot)
        await self._cur.add_usable_by(self._ctx)
        self._embeds[self._idx] = self._cur

        components = self._get_buttons()
        for c in components:
            c.disabled = True

        await self._message.edit(embed=self._cur, components=[components])

    def _get_buttons(self):
        components = copy.copy(self._buttons)
        if self._idx == 0:
            components.pop(0)

        if self._idx == len(self._embeds) - 1:
            components.pop()

        return components