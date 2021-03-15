from typing import Tuple
from discord import HTTPException
from discord.ext import commands
from .converters import JSONConverter
from ..utils import embeds
from ..utils.fmt_strings import CODE_BLOCK
from ..utils.menus import ConfirmMenu, CodeBlockMenu
from ..utils.data_manip import flatten_dict, split_string, unflatten_dict

CHAR_LIMIT = 1500

class ConfigCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="config")
    @commands.has_permissions(manage_guild=True)
    async def _config(self, ctx: commands.Context) -> None:
        """
        The root command for the group
        :param ctx: The context the command is being executed in
        :type ctx: commands.Context
        """
        if ctx.invoked_subcommand is None:
            pass

    @_config.command()
    async def view(self, ctx: commands.Context, *subs: Tuple[str]) -> None:
        """
        Lets you view the config. You can specify up to a certain path
        :param ctx: The context the command is being executed in
        :type ctx: commands.Context
        :param subs: The sub paths
        :type subs: Tuple[Any]
        """

        #TODO: Figure out a way to make this work as a decorator
        for member in ctx.channel.members:
            if not member.permissions_in(ctx.channel).manage_guild and not member.bot:
                confirm = await ConfirmMenu(
                    "This command can show sensitive information. There are people who can access this channel that do not have the manage server permission, do you wish to still run the command?").prompt(
                    ctx)
                if not confirm:
                    await ctx.send(embed=embeds.ErrorEmbed("Cancelled!"))
                    return

        current_item: dict = self.bot.config

        try:
            for sub in subs:
                current_item = current_item[sub]
        except KeyError:
            await ctx.send(
                embed=embeds.ErrorEmbed(f"The path at {'.'.join(subs)} is invalid, sending up to last valid path"))

        flattened = flatten_dict(current_item)

        res_str = ""
        for k, v in flattened.items():
            if isinstance(v, str):
                res_str += f"{k}: '{v}'\n"
            else:
                res_str += f"{k}: {v}\n"

        try:
            await ctx.send(CODE_BLOCK.format("py", res_str))
        except HTTPException:
            parts = split_string(res_str, CHAR_LIMIT)
            menu = CodeBlockMenu(parts)
            await menu.start(ctx)

    @_config.command()
    async def set(self, ctx: commands.Context, key: str, *, value: JSONConverter) -> None:
        """
        Allows to set the value of a config field
        :param ctx: The context with which the command is being invoked
        :type ctx: commands.Context
        :param key: The key to set
        :type key: str
        :param value: The value to set it to
        :type value: str
        """
        flattened = flatten_dict(self.bot.config)

        try:
            if type(value) != type(flattened[key]):
                confirm = await ConfirmMenu(
                    f"The type of the value you provided: {value} does not match the type of the current value. Are you sure you'd like to change it?") \
                    .prompt(ctx)

                if not confirm:
                    await ctx.send(embed=embeds.ErrorEmbed("Cancelled!"))
                    return
            flattened[key] = value
        except KeyError:
            await ctx.send(embed=embeds.ErrorEmbed(f"The key: {key} is invalid!"))
            return

        self.bot.config.update(unflatten_dict(flattened))
        self.bot.config.save()
        await ctx.send(embed=embeds.SuccessEmbed(f"Set key: {key} to value: {value}",
                                                 description="Note, some changes will not take effect until restart!"))
