from discord.ext import commands
from litebot.utils import embeds
from litebot.utils.fmt_strings import INLINE_CODE_BLOCK, COMMAND_PATH


class HelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return INLINE_CODE_BLOCK.format(f"{self.clean_prefix}{command.qualified_name} {command.signature}")

    def get_command_path(self, command):
        return COMMAND_PATH.format(self.clean_prefix, command.full_parent_name, command.name)

    def get_help_brief(self, command):
        return f"{self.get_command_signature(command)}: {command.short_doc}"

    async def send_bot_help(self, mapping):
        embed = embeds.InfoEmbed("LiteBot Help Panel")
        for command in [c[0] for c in mapping.values()]:
            try:
                await command.can_run(self.context)
            except commands.CheckFailure:
                continue
            if isinstance(command, commands.Group):
                sigs = [self.get_help_brief(c) for c in command.walk_commands()]
                embed.add_field(name=command.name, value="\n".join(sigs), inline=False)
            else:
                embed.add_field(name=command.name, value=self.get_help_brief(command), inline=False)

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        await command.can_run(self.context)
        embed = embeds.InfoEmbed(f"Help for command: {command.name}", description=self.get_command_signature(command))
        embed.add_field(name="Command Usage:", value=command.help)

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        await group.can_run(self.context)
        sigs = [self.get_command_signature(c) for c in group.walk_commands()]
        embed = embeds.InfoEmbed(f"Help for group: {group.name}", description="\n".join(sigs))
        for command in group.walk_commands():
            embed.add_field(name=self.get_command_path(command), value=command.help, inline=False)

        await self.get_destination().send(embed=embed)

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=embeds.ErrorEmbed("You do not have permission to perform this command"))