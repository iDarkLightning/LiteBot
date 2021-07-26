from discord_components import Button, ButtonStyle, InteractionType

from litebot.core.context import Context
from litebot.utils.embeds import ErrorEmbed, InfoEmbed
from litebot.utils.timer import Timer
from plugins.standard.panel.embeds import PanelEmbed


class PanelMenu:
    class InteractionTypes:
        START = "start"
        RESTART = "restart"
        STOP = "stop"
        KILL = "kill"

    def __init__(self, ctx: Context, embed: PanelEmbed, timeout=120):
        self._ctx = ctx
        self._embed = embed
        self._server = embed.server
        self._timeout = timeout
        self._timer = None
        self._message = None
        self._task = None
        self._buttons = [
            [
                Button(style=ButtonStyle.green, label="▶ Start", id=PanelMenu.InteractionTypes.START),
                Button(style=ButtonStyle.green, label="🔄 Restart", id=PanelMenu.InteractionTypes.RESTART),
                Button(style=ButtonStyle.red, label="⏹ Stop", id=PanelMenu.InteractionTypes.STOP),
                Button(style=ButtonStyle.red, label="💀 Kill", id=PanelMenu.InteractionTypes.KILL)
            ]
        ]

    async def start(self):
        self._message = await self._ctx.send(embed=self._embed, components=self._buttons)
        self._task = self._ctx.bot.loop.create_task(self._loop())

        self._timer = Timer(self._done, self._timeout)

    async def _loop(self):
        while True:
            def check(m):
                return m.id == self._message.id and self._message.id and m.channel == self._ctx.channel and m.author == self._ctx.author

            interaction = await self._ctx.bot.wait_for("button_click", check=check)
            await interaction.respond(type=InteractionType.DeferredChannelMessageWithSource)
            await self._timer.reset()

            interaction_type = interaction.raw_data["d"]["data"]["custom_id"]
            await getattr(self, f"_{interaction_type}", lambda i: None)(interaction)

    async def _start(self, interaction):
        if self._server.status().online:
            return await interaction.edit(embed=ErrorEmbed(f"{self._server.name.upper()} is already online!"))

        async with self._ctx.typing():
            await interaction.edit(embed=InfoEmbed(f"Starting {self._server.name.upper()}"))
            await self._server.start()
            await interaction.edit(embed=InfoEmbed(f"Started {self._server.name.upper()}"))

    async def _stop(self, interaction):
        if not self._server.status().online:
            return await interaction.edit(embed=ErrorEmbed(f"{self._server.name.upper()} is already offline!"))

        async with self._ctx.typing():
            await interaction.edit(embed=InfoEmbed(f"Stopping {self._server.name.upper()}"))
            await self._server.stop()
            await interaction.edit(embed=InfoEmbed(f"Stopped {self._server.name.upper()}"))

    async def _restart(self, interaction):
        if not self._server.status().online:
            return await interaction.edit(embed=ErrorEmbed(f"{self._server.name.upper()} is offline, and cannot be restarted!"))

        await self._server.restart()
        await interaction.edit(embed=InfoEmbed(f"Restarted {self._server.name.upper()}"))

    async def _kill(self, interaction):
        if not self._server.status().online:
            return await interaction.edit(embed=ErrorEmbed(f"{self._server.name.upper()} is offline"))

        async with self._ctx.typing():
            await interaction.edit(embed=InfoEmbed(f"Killing {self._server.name.upper()}"))
            await self._server.kill()
            await interaction.edit(embed=InfoEmbed(f"Killed {self._server.name.upper()}"))

    async def _done(self):
        self._task.cancel()

        buttons = self._buttons[0]
        for b in buttons:
            b.disabled = True

        await self._message.edit(components=[buttons])