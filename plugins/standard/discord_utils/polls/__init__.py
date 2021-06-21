from typing import Optional

import discord
from discord.ext import commands
from mongoengine import NotUniqueError

from litebot.core import Cog, Context
from litebot.models import TrackedEvent
from litebot.utils import embeds
from litebot.utils.menus import CodeBlockMenu, ConfirmMenu

from plugins.standard.discord_utils.polls.errors import PollCommandError
from plugins.standard.discord_utils.polls.poll_preset_model import PollPreset
from plugins.standard.discord_utils.polls.utils import role_or_member, ORDINAL_A, Poll, PollPresetConverter


class PollCommand(Cog):
    @Cog.setting(name="Poll Command", description="Easily create polls on discord!")
    @commands.group(name="poll")
    async def _poll(self, ctx: Context) -> None:
        """
        This is the root command for the poll group.
        This command serves no function without
        a subcommand, but will send the help message for this group.
        Essentially invokes `help poll`
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help("poll")

    @_poll.command(name="create")
    async def _poll_create(self, ctx: Context, channel: Optional[discord.TextChannel], *, poll: Poll):
        """
        You have two options for creating a poll. You can create a simple Y/N poll, or a poll with multiple choices.

        The command uses a "command line" syntax. Use the following syntax to create a poll

        `channel`: The channel to post the poll message in.

        `--prompt` or `-p`: The question for the poll.
        `--option` or `-o`: Can be used a maximum of 26 times, for 26 different options. If this is not provided, then the prompt will only have Y/N options
        `--mention` or `-m`: Members or Roles to mention in the message.
        """

        channel = channel if channel else ctx.channel

        if not poll.options:
            message = await channel.send(poll.mentions,embed=embeds.InfoEmbed(poll.prompt))
            await message.add_reaction("\N{THUMBS UP SIGN}")
            await message.add_reaction("\N{THUMBS DOWN SIGN}")
        else:
            message = await channel.send(poll.mentions, embed=embeds.InfoEmbed(poll.prompt, description=poll.formatted_options))
            for emoji in poll.options.values():
                await message.add_reaction(emoji)

        TrackedEvent(tracking_id=message.id, event_tag="poll").save()

    @_poll.group(name="preset")
    async def _poll_preset(self, ctx: commands.Context) -> None:
        """
        This is the root command for the poll preset group.
        This command serves no function without
        a subcommand, but will send the help message for this group.
        Essentially invokes `help poll preset`
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help("poll preset")

    @_poll_preset.command(name="view")
    async def _poll_preset_view(self, ctx: commands.Context) -> discord.Message:
        """
        This command lets you view all the currently available presets
        """
        if not (presets := PollPreset.objects()):
            return await ctx.send(embed=embeds.ErrorEmbed("There are no available presets!"))

        await CodeBlockMenu([f"Preset Name: {preset.name}\nPrompt: {preset.prompt}\nOptions:\n-" + "\n-".join(
            preset.options) for preset in presets], "").start(ctx)

    @_poll_preset.command(name="load", aliases=["post"])
    async def _poll_preset_post(self, ctx: commands.Context, channel: Optional[discord.TextChannel], *, poll: PollPresetConverter) -> None:
        """
        Post an existing preset for a poll.

        The command uses a "command line" syntax. Use the following syntax to create a poll

        `channel`: The channel to post the message in
        `--name` or `-n`: The name of the preset to load
        `--member` or `-m`: The member to be provided to the preset
        `--role` or `-r`: The role to be provided to the preset
        """
        channel = channel or ctx.channel

        message = await channel.send(f"{poll.prompt}\n" + poll.formatted_options)

        for emoji in poll.options.values():
            await message.add_reaction(emoji)

    @_poll_preset.command(name="save", aliases=["create"])
    async def _poll_preset_save(self, ctx: commands.Context, *, poll: Poll) -> discord.Message:
        """
        Creates a new preset for polls.

        The command uses a "command line" syntax. The syntax is the exact same as creating regular polls.
        However, you have access to a member and role object within your poll. You can access those objects like such:

        --prompt {role.mention} How is your day? --option Better than {member.name}'s --option Bad
        """
        if not poll.name:
            raise PollCommandError("Poll Presets must have a name!")

        if not await ConfirmMenu(f"{poll.prompt}\n" + poll.formatted_options).prompt(ctx):
            return await ctx.send(embed=embeds.ErrorEmbed("Aborted!"))

        try:
            PollPreset(name=poll.name, prompt=poll.prompt, options=poll.options.keys()).save()
        except NotUniqueError:
            return await ctx.send(embed=embeds.ErrorEmbed("There is already a preset with this name!"))

        await ctx.send(embed=embeds.SuccessEmbed(f"Created a new preset: {poll.name}"))

    @_poll_preset.command(name="delete")
    @commands.has_permissions(manage_guild=True)
    async def _poll_preset_delete(self, ctx: commands.Context, *, preset_name: str) -> discord.Message:
        """
        This command lets you delete a current preset.
        `preset_name` The name of the preset you'd like to delete
        """
        if not (poll := PollPreset.objects(name=preset_name).first()):
            return await ctx.send(embed=embeds.ErrorEmbed("There is no poll preset with this name!"))

        poll.delete()
        await ctx.send(embed=embeds.SuccessEmbed(f"Deleted the preset: {preset_name}"))

    async def cog_command_error(self, ctx: Context, err):
        if isinstance(err, PollCommandError):
            await ctx.send(embed=embeds.ErrorEmbed(str(err)))

    @Cog.listener(type=Cog.ListenerTypes.DISCORD)
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        """
        This listener removes a poll from the current tracked events if a poll message is deleted.
        """
        matched_events: list[TrackedEvent] = TrackedEvent.objects(tracking_id=payload.message_id, event_tag="poll")
        for event in matched_events:
            event.delete()

    @Cog.listener(type=Cog.ListenerTypes.DISCORD)
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        """
        This listener removes all other reactions from poll messages in order to remove confusion.
        """
        matched_events: list[TrackedEvent] = TrackedEvent.objects(tracking_id=payload.message_id, event_tag="poll")
        for event in matched_events:
            channel: discord.TextChannel = await self._bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(event.tracking_id)

            for reaction in message.reactions:
                if self._bot.user not in (await reaction.users().flatten()):
                    await reaction.clear()
