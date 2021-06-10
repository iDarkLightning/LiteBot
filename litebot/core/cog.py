from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

from discord.ext.commands import Cog as DPYCog, CogMeta as DPYCogMeta, Command, Context
from discord.ext.commands._types import _BaseCommand
from sanic import Blueprint

from litebot.core.minecraft.commands.action import ServerAction, ServerCommand
from litebot.core.settings import Setting, SettingsManager, SettingTypes

if TYPE_CHECKING:
    from litebot.litebot import LiteBot

class CogMeta(DPYCogMeta):
    def __new__(cls, *args, **kwargs):
        name, bases, attrs = args
        attrs["__cog_name__"] = kwargs.pop("name", name)
        attrs["__cog_settings__"] = kwargs.pop("command_attrs", {})

        description = kwargs.pop("description", None)
        if description is None:
            description = inspect.cleandoc(attrs.get("__doc__", ""))
        attrs["__cog_description__"] = description

        discord_commands = {}
        mc_commands = {}
        listeners = {}
        settings = set()
        blueprint = Blueprint(name)
        no_bot_cog = "Commands or listeners must not start with cog_ or bot_ (in method {0.__name__}.{1})"

        new_cls = super().__new__(cls, name, bases, attrs, **kwargs)
        for base in reversed(new_cls.__mro__):
            for elem, value in base.__dict__.items():
                if elem in discord_commands:
                    del discord_commands[elem]
                if elem in listeners:
                    del listeners[elem]
                if elem in mc_commands:
                    del mc_commands[elem]

                is_static_meth = isinstance(value, staticmethod)
                if is_static_meth:
                    value = value.__func__
                if isinstance(value, Command):
                    command = value.root_parent if value.root_parent else value
                    if hasattr(command.callback, "__setting__"):
                        if is_static_meth:
                            raise TypeError("Command in method {0}.{1!r} must not be staticmethod.".format(base, elem))
                        if elem.startswith(("cog_", "bot_")):
                            raise TypeError(no_bot_cog.format(base, elem))
                        discord_commands[elem] = value
                        settings.add(command.callback.__setting__)
                    else:
                        raise TypeError("Command in method {0}.{1!r} must be a setting!".format(base, elem))
                elif isinstance(value, ServerCommand):
                    command = value.root_parent
                    if hasattr(command, "__setting__"):
                        if is_static_meth:
                            raise TypeError("Command in method {0}.{1!r} must not be staticmethod.".format(base, elem))
                        if elem.startswith(("cog_", "bot_")):
                            raise TypeError(no_bot_cog.format(base, elem))
                        mc_commands[elem] = value
                        settings.add(command.__setting__)
                    else:
                        raise TypeError("Command in method {0}.{1!r} must be a setting!".format(base, elem))
                elif inspect.iscoroutinefunction(value):
                    if hasattr(value, "__cog_listener__"):
                        if elem.startswith(('cog_', 'bot_')):
                            raise TypeError(no_bot_cog.format(base, elem))

                        listeners[elem] = value
                        if hasattr(value, "__setting__"):
                            settings.add(value.__setting__)

        new_cls.__settings__ = list(settings)
        new_cls.__discord_commands__ = list(discord_commands.values())
        new_cls.__mc_commands__ = list(mc_commands.values())
        new_cls.__cog_commands__ = list({**discord_commands, **mc_commands}.values())
        new_cls.__sanic_blueprint__ = blueprint

        listeners_list = []
        for listener in listeners.values():
            for listener_name in listener.__cog_listener_names__:
                listeners_list.append((listener_name, listener.__type__, listener.__name__))

        new_cls.__cog_listeners__ = listeners_list
        return new_cls

class Cog(DPYCog, metaclass=CogMeta):
    # This method is pretty much word for word copy pasted from `DPYCog.__new__` but changed to reflect the change
    # between __discord_commands__ and __mc_commands__

    class ListenerTypes:
        DISCORD = "discord"
        MINECRAFT = "minecraft"

    def __new__(cls, *args, **kwargs):
        self = object.__new__(cls)

        cmd_attrs = cls.__cog_settings__

        self.__discord_commands__ = tuple(c._update_copy(cmd_attrs) for c in cls.__discord_commands__)
        lookup = {
            cmd.qualified_name: cmd
            for cmd in self.__discord_commands__
        }

        for command in self.__discord_commands__:
            setattr(self, command.callback.__name__, command)
            parent = command.parent
            if parent is not None:
                parent = lookup[parent.qualified_name]

                parent.remove_command(command.name)
                parent.add_command(command)

        for command in self.__mc_commands__:
            command.update_cog_ref(self)

        return self

    def get_listeners(self):
        return [(name, getattr(self, method_name), type_) for name, type_, method_name in self.__cog_listeners__]

    @classmethod
    def listener(cls, type, name=None):
        if name is not None and not isinstance(name, str):
            raise TypeError('Cog.listener expected str but received {0.__class__.__name__!r} instead.'.format(name))

        def decorator(func):
            actual = func
            if isinstance(actual, staticmethod):
                actual = actual.__func__
            if not inspect.iscoroutinefunction(actual):
                raise TypeError("Listener function must be a coroutine function.")

            if type == Cog.ListenerTypes.DISCORD:
                if hasattr(func, "__type__") and func.__type__ == Cog.ListenerTypes.MINECRAFT:
                    raise TypeError("Cog.listener can only be of one type!")
                func.__type__ = Cog.ListenerTypes.DISCORD
            elif type == Cog.ListenerTypes.MINECRAFT:
                if hasattr(func, "__type__") and func.__type__ == Cog.ListenerTypes.DISCORD:
                    raise TypeError("Cog.listener can only be one type!")
                func.__type__ = Cog.ListenerTypes.MINECRAFT
            else:
                raise TypeError("Cog.listener type must be Cog.ListenerTypes.DISCORD or Cog.ListenerTypes.MINECRAFT")

            actual.__cog_listener__ = True
            to_assign = name or actual.__name__
            try:
                actual.__cog_listener_names__.append(to_assign)
            except AttributeError:
                actual.__cog_listener_names__ = [to_assign]

            return func
        return decorator

    @classmethod
    def setting(cls, **kwargs):
        def decorator(func):
            if isinstance(func, _BaseCommand):
                kwargs["type"] = SettingTypes.DISC_COMMAND
                func.callback.__setting__ = Setting(func, **kwargs)
            elif isinstance(func, ServerCommand):
                kwargs["type"] = SettingTypes.MC_COMMAND
                func.__setting__ = Setting(func, **kwargs)
            elif hasattr(func, "__cog_listener__"):
                kwargs["type"] = SettingTypes.EVENT
                func.__setting__ = Setting(func, **kwargs)
            else:
                raise TypeError("Setting must be a discord/mc command or a listener!")
            return func
        return decorator

    def _inject(self, bot: LiteBot):
        cls = self.__class__
        self._bot = bot
        self._plugin = bot.processing_plugin

        self._plugin.blueprint_group.blueprints.append(self.__sanic_blueprint__)

        bot.settings_manager.add_settings(bot.processing_plugin.meta.repr_name, self.__settings__)

        for index, command in enumerate(self.__discord_commands__):
            command.cog = self
            command.plugin = self._plugin
            if command.parent is None:
                try:
                    setting = command.callback.__setting__
                    if setting.enabled:

                        def id_checks(ctx: Context):
                            setting_ = ctx.command.callback.__setting__
                            if ctx.author.id in setting_.id_checks:
                                return True
                            if not setting_.id_checks:
                                return True

                            return set([role.id for role in ctx.author.roles]) & set(setting_.id_checks)

                        command.add_check(id_checks)
                        bot.add_command(command)
                except Exception as e:
                    for to_undo in self.__discord_commands__[:index]:
                        if to_undo.parent is None:
                            bot.remove_command(to_undo.name)
                    raise e

        for command in self.__mc_commands__:
            if command.__setting__.enabled:
                command.op_level = command.__setting__.op_level
                bot.add_command(command)

        if cls.bot_check is not Cog.bot_check:
            bot.add_check(self.bot_check)

        if cls.bot_check_once is not Cog.bot_check_once:
            bot.add_check(self.bot_check_once, call_once=True)

        for name, type_, method_name in self.__cog_listeners__:
            try:
                if getattr(self, method_name).__setting__.enabled:
                    if type_ == Cog.ListenerTypes.DISCORD:
                        bot.add_listener(getattr(self, method_name), name)
                    else:
                        bot.add_server_listener(getattr(self, method_name), name)
            except AttributeError:
                if type_ == Cog.ListenerTypes.DISCORD:
                    bot.add_listener(getattr(self, method_name), name)
                else:
                    bot.add_server_listener(getattr(self, method_name), name)

        return self

    def _eject(self, bot: LiteBot):
        cls = self.__class__

        try:
            for command in self.__discord_commands__:
                if command.parent is None:
                    bot.remove_command(command.name)

            for command in self.__mc_commands__:
                bot.remove_command(command.full_name)

            for name, type_, meth_name in self.__cog_listeners__:
                if type_ == Cog.ListenerTypes.DISCORD:
                    bot.remove_listener(getattr(self, meth_name))
                else:
                    bot.remove_server_listener(getattr(self, meth_name), name)

                if cls.bot_check is not Cog.bot_check:
                    bot.remove_check(self.bot_check)

                if cls.bot_check_once is not Cog.bot_check_once:
                    bot.remove_check(self.bot_check_once, call_once=True)
        finally:
            try:
                self.cog_unload()
            except Exception:
                pass