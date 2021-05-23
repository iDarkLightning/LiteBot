from discord.ext.commands import Cog as DPYcog

from litebot.core.minecraft.commands.action import ServerAction, ServerCommand


class Cog(DPYcog):
    __cog_name__: str

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)

        func_list = []
        for func in dir(self):
            try:
                func_list.append(getattr(self, func))
            except AttributeError:
                continue

        server_actions = [func for func in func_list if isinstance(func, ServerAction)]
        self.__server_actions__ = server_actions

        return self

    def _inject(self, bot):
        super()._inject(bot)

        for server_action in self.__server_actions__:
            server_action.cog = self

            if isinstance(server_action, ServerCommand):
                if server_action.subs:
                    for val in server_action.subs.values():
                        val.cog = self

                bot.add_command(server_action)
            else:
                bot.add_event(server_action)

        return self

    def _eject(self, bot):
        super()._eject(bot)

        for server_action in self.__server_actions__:
            if isinstance(server_action, ServerCommand):
                bot.remove_command(server_action.full_name)
            else:
                bot.remove_event(server_action.name, self)

        return self