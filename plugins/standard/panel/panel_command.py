import json

from discord.ext import commands
from discord_components import Button, ButtonStyle

from litebot.core import Cog
from litebot.core.context import Context
from litebot.core.minecraft import ServerEventContext
from litebot.core.minecraft.commands.payload import ConsoleMessagePayload, HostConnectPayload
from litebot.utils.embeds import ErrorEmbed, InfoEmbed
from plugins.standard.panel.embeds import PanelEmbed
from plugins.standard.panel.menus import PanelMenu


class PanelCommand(Cog):
    def __init__(self):
        self.server_logs: dict[str, list[str]] = {}

    @Cog.listener(type=Cog.ListenerTypes.MINECRAFT, name="on_console_message")
    async def _console_message(self, ctx: ServerEventContext, payload: ConsoleMessagePayload):
        if ctx.server.name in self.server_logs:
            self.server_logs[ctx.server.name].append(payload.message)
        else:
            self.server_logs[ctx.server.name] = [payload.message]

    @Cog.listener(type=Cog.ListenerTypes.MINECRAFT, name="on_host_connect")
    async def _host_connect(self, ctx: ServerEventContext, payload: HostConnectPayload):
        self.server_logs[ctx.server.name] = payload.log


    @Cog.setting(name="Panel Command", description="A panel embedded in discord to control your servers!")
    @commands.command(name="panel")
    async def _panel(self, ctx: Context, server_name: str):
        """
        An interactive panel to control your server!
        `server_name`: The name of the server to view the panel for
        """
        server = self._bot.servers.get_server(ctx, server_name)
        if not server.host_connected:
            return await ctx.send(embed=ErrorEmbed("The server host is currently not connected!"))

        embed = PanelEmbed(ctx.author, self.server_logs.get(server.name, []), server)

        menu = PanelMenu(ctx, embed)
        await menu.start()

    @Cog.setting(name="Start Server", description="Start a server")
    @commands.command(name="start")
    async def _start(self, ctx: Context, server_name: str):
        """
        Start a server
        `server_name`: The name of the server to start
        """
        server = self._bot.servers.get_server(ctx, server_name)

        if server.status().online:
            return await ctx.send(embed=ErrorEmbed(f"{server.name.upper()} is already online!"))

        async with ctx.typing():
            msg = await ctx.send(embed=InfoEmbed(f"Starting {server.name.upper()}"))
            await server.start()
            await msg.delete()
            await ctx.send(embed=InfoEmbed(f"Started {server.name.upper()}"))

    @Cog.setting(name="Stop Server", description="Stop a server")
    @commands.command(name="stop")
    async def _stop(self, ctx: Context, server_name: str):
        """
        Stop a server
        `server_name`: The name of the server to stop
        """
        server = self._bot.servers.get_server(ctx, server_name)

        if not server.status().online:
            return await ctx.send(embed=ErrorEmbed(f"{server.name.upper()} is already offline!"))

        async with ctx.typing():
            msg = await ctx.send(embed=InfoEmbed(f"Stopping {server.name.upper()}"))
            await server.stop()
            await msg.delete()
            await ctx.send(embed=InfoEmbed(f"Stopped {server.name.upper()}"))

    @Cog.setting(name="Restart Server", description="Restart a server")
    @commands.command(name="restart")
    async def _restart(self, ctx: Context, server_name: str):
        """
        Restart a server
        `server_name`: The name of the server to restart
        """
        server = self._bot.servers.get_server(ctx, server_name)

        if not server.status().online:
            return await ctx.send(embed=ErrorEmbed(f"{server.name.upper()} is offline, and cannot be restarted!"))

        await server.restart()
        await ctx.send(embed=InfoEmbed(f"Restarted {server.name.upper()}"))

    @Cog.setting(name="Kill Server", description="Kill a server")
    @commands.command(name="kill")
    async def _kill(self, ctx: Context, server_name: str):
        """
        Kill a server
        `server_name`: The name of the server to kill
        """
        server = self._bot.servers.get_server(ctx, server_name)

        if not server.status().online:
            return await ctx.send(embed=ErrorEmbed(f"{server.name.upper()} is already offline!"))

        async with ctx.typing():
            msg = await ctx.send(embed=InfoEmbed(f"Killing {server.name.upper()}"))
            await server.kill()
            await msg.delete()
            await ctx.send(embed=InfoEmbed(f"Killed {server.name.upper()}"))