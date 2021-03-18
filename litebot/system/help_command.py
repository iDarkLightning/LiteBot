from collections import Mapping
from typing import Optional, List
from discord.ext import commands
from litebot.utils import embeds
from litebot.utils.fmt_strings import INLINE_CODE_BLOCK, COMMAND_PATH


class HelpCommand(commands.HelpCommand):
    def get_command_signature(self, command: commands.Command) -> str:
        """
        Get's the command's signature
        :param command: The command to get the signature for
        :type command: commands.Command
        :return: The command's signature
        :rtype: str
        """
        return INLINE_CODE_BLOCK.format(f"{self.clean_prefix}{command.qualified_name} {command.signature}")

    def get_command_path(self, command: commands.Command) -> str:
        """
        Get's the full path to a command
        :param command: The command to get the path to
        :type command: commands.Command
        :return: The full path to the command including the prefix
        :rtype: str
        """
        return COMMAND_PATH.format(self.clean_prefix, command.full_parent_name, command.name)

    def get_help_brief(self, command: commands.Command) -> str:
        """
        Get's the command's signature and the command's brief
        :param command: The command to get the brief for
        :type command: commands.Command
        :return: The command's brief help statement
        :rtype: str
        """
        return f"{self.get_command_signature(command)}: {command.short_doc}"

    async def send_bot_help(self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]]) -> None:
        """
        Handles response for the plain help command `help`
        :param mapping: A mapping of the registered cogs and commands
        :type mapping: Mapping[Optional[commands.Cog], List[commands.Command]]
        """
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

    async def send_command_help(self, command: commands.Command) -> None:
        """
        Handles response for help command for individual commands `help command`
        :param command: The command to provide help for
        :type command: commands.Command
        """
        await command.can_run(self.context)
        embed = embeds.InfoEmbed(f"Help for command: {command.name}", description=self.get_command_signature(command))
        embed.add_field(name="Command Usage:", value=command.help)

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group: commands.Group) -> None:
        """
        Handles response for help command for command groups `help group`
        :param group: The group to provide help for
        :type group: commands.Group
        """
        await group.can_run(self.context)
        sigs = [self.get_command_signature(c) for c in group.walk_commands()]
        embed = embeds.InfoEmbed(f"Help for group: {group.name}", description="\n".join(sigs))
        for command in group.walk_commands():
            embed.add_field(name=self.get_command_path(command), value=command.help, inline=False)

        await self.get_destination().send(embed=embed)

    async def on_help_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """
        Handles all errors that occur as a result of the help command
        :param ctx: The context in which the command was executed
        :type ctx: commands.Context
        :param error: The error that was raised
        :type error: Exception
        """
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=embeds.ErrorEmbed("You do not have permission to perform this command"))