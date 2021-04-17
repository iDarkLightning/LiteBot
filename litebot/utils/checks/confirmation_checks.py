from litebot.errors import ConfirmationDenied
from litebot.utils.menus import ConfirmMenu
from litebot.utils import embeds
from discord.ext import commands

async def manage_server_confirmation(instance, ctx: commands.Context) -> None:
    """
    Prompts the user if they want to execute the command in the channel,
    if there are people who can see the channel without the
    `manage_server` permission
    :param instance: The instance that the confirmation is being checked on
    :type instance: LiteBot
    :param ctx: The context the command is running with
    :type ctx: commands.Context
    """
    for member in ctx.channel.members:
        if not member.permissions_in(ctx.channel).manage_guild and not member.bot:
            confirm = await ConfirmMenu(
                "This command can show sensitive information. There are people who can access this channel that do not have the manage server permission, do you wish to still run the command?").prompt(
                ctx)
            if not confirm:
                await ctx.send(embed=embeds.ErrorEmbed("Cancelled!"))
                raise ConfirmationDenied