from typing import Tuple, Union

import discord
from discord import HTTPException
from discord.ext import commands
from .converters import JSONConverter
from ..utils import embeds
from ..utils.config import BaseConfig
from ..utils.data_manip import flatten_dict, split_string, unflatten_dict
from ..utils.fmt_strings import CODE_BLOCK
from ..utils.menus import CodeBlockMenu, ConfirmMenu

CHAR_LIMIT = 1500

async def config_view(config: BaseConfig, ctx: commands.Context) -> None:
    """
    Takes a dictionary, formats and sends it
    This is designed to be used in a command,
    as it interacts directly with the user.
    :param config: The config file to send
    :type config: BaseConfig
    :param ctx: The context the command is being executed in
    :type ctx: commands.Context
    """
    with open(config.file_path) as f:
        file = discord.File(f)
        await ctx.send(file=file)


async def config_save(config: BaseConfig, ctx: commands.Context, key: str, value: JSONConverter) -> None:
    """
    Takes a dictionary, a key, sets the value.
    This is designed to be used in a command,
    as it interacts directly with the user.
    :param config: The config object to set
    :type config: BaseConfig
    :param ctx: The context the command is being executed in
    :type ctx: commands.Context
    :param key: The key to set in the config
    :type key: str
    :param value: The value to set the key to
    :type value: JSONConverter
    """
    flattened = flatten_dict(config)

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

    config.update(unflatten_dict(flattened))
    config.save()
    await ctx.send(embed=embeds.SuccessEmbed(f"Set key: {key} to value: {value}",
                                             description="Note, some changes will not take effect until restart!"))