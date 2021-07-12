from typing import Union

from discord.ext import commands
from discord.ext.commands import Group, Command

from litebot.core import Cog, Context, Plugin, ServerCommand
from litebot.utils.embeds import InfoEmbed, ErrorEmbed


class HelpCommand(Cog, required=True):

    @commands.command(name="help")
    async def _help(self, ctx: Context, specifier=None):
        """
        View help messages for all the various commands:

        Args:
            `specifier`: The plugin/cog/command to specifiy the help message for
        """
        if not specifier:
            return await self._base(ctx)

        if plugin := self._bot.plugin_manager[specifier]:
            return await self._plugin(ctx, plugin)

        if cog := self._bot.cogs.get(specifier):
            return await self._cog(ctx, cog)

        if command := self._bot.get_command(specifier):
            return await self._command(ctx, command)

        return await ctx.send(embed=ErrorEmbed(f"Nothing found with the specifier: {specifier}"))

    async def _base(self, ctx: Context):
        plugins = self._bot.plugin_manager.all_plugins.values()

        embed = InfoEmbed("Help")

        for plugin in plugins:
            embed.add_field(
                name=plugin.meta.name,
                value=plugin.description + f"\n`help {plugin.meta.repr_name}`",
                inline=False
            )

        await ctx.send(embed=embed)

    async def _plugin(self, ctx: Context, plugin: Plugin):
        embed = InfoEmbed(f"Help for {plugin.meta.name}")

        for cog in plugin.cogs:
            embed.add_field(
                name=cog.__cog_name__,
                value=cog.__cog_description__ + f"\n`help {cog.__cog_name__}`",
                inline=False
            )

        await ctx.send(embed=embed)

    async def _cog(self, ctx: Context, cog: Cog):
        embed = InfoEmbed(f"Help for {cog.__cog_name__}")

        for cmd in cog.walk_commands():
            if isinstance(cmd, ServerCommand) or cmd.root_parent:
                continue

            msg = cmd.short_doc + f"\n`help {cmd.name}`" if isinstance(cmd, Group) else cmd.help

            if await cmd.can_run(ctx):
                embed.add_field(
                    name=f"{cmd.name.capitalize()} Command:",
                    value=msg,
                    inline=False
                )

        await ctx.send(embed=embed)

    async def _command(self, ctx: Context, command: Union[Command, Group]):
        embed = InfoEmbed(f"Help for {command.name}")

        embed.add_field(
            name=f"{command.name.capitalize()} Command:",
            value=f"`{command.qualified_name} {command.signature}`\n" + command.help,
            inline=False
        )

        if isinstance(command, Group):
            for sub in command.walk_commands():
                embed.add_field(
                    name=f"{' '.join([c.capitalize() for c in sub.qualified_name.split(' ')])}:",
                    value=f"`{sub.qualified_name} {sub.signature}`\n" + sub.help,
                    inline=False
                )

        await ctx.send(embed=embed)


