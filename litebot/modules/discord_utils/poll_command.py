import re
import discord
from typing import Union, Tuple, List, Optional, Any
from mongoengine.errors import NotUniqueError
from discord.ext import commands
from discord.ext.commands import MemberConverter, MemberNotFound, RoleConverter, RoleNotFound

from litebot.core import Cog
from litebot.utils.checks import role_checks
from litebot.models import PollPreset
from litebot.models import TrackedEvent
from litebot.errors import PollCommandError
from litebot.utils import embeds
from litebot.utils.menus import CodeBlockMenu

ORDINAL_A = 127462

async def parse_poll_message(ctx: commands.Context, poll_str: str) -> Union[Tuple[str, list], Tuple[str, dict, list]]:
    """
    Parses a poll message into a prompt and options
    :param ctx: The context that command was executed in
    :type ctx: commands.Context
    :param poll_str: The poll string to parse
    :type poll_str: str
    :return: The parsed poll, consisting of a prompt, the options and the users to mention
    :rtype: Union[Tuple[str, list], Tuple[str, dict, list]]
    """
    if not poll_str:
        raise PollCommandError

    poll_reg = re.compile(r"[{\[][^\[]+[}\]]")
    flag_reg = re.compile(r"-{1,2}mention [\w#/\s]+")

    flags = flag_reg.findall(poll_str)
    matches = poll_reg.findall(poll_str)
    mentions = []

    if flags:
        parsed_mentions = [i.split(" ")[1] for i in flags]
        for mention in parsed_mentions:
            try:
                mentions.append((await MemberConverter().convert(ctx, mention)).mention)
            except MemberNotFound:
                mentions.append((await RoleConverter().convert(ctx, mention)).mention)
            except RoleNotFound:
                raise PollCommandError

    if not matches:
        return re.sub(flag_reg, "", poll_str), mentions

    question = ""
    prompts = {}

    for match in matches:
        if re.match("{[^\[]+}", match) and not question:
            question = re.sub("[{}]+", "", match)
        elif re.match("\[[^\[]+]", match) and len(prompts) < 27:
            prompts[(re.sub("[\[\]]+", "", match))] = chr(len(prompts) + ORDINAL_A)

    return question, prompts, mentions

def parse_preset(poll: PollPreset, role: Optional[discord.Role], member: Optional[discord.Member]) -> tuple[Any, dict[Any, str]]:
    """
    This parses a preset and inserts the role and the member into the preset string.
    :param poll: The poll preset
    :type poll: PollPreset
    :param role: The role to insert into the preset
    :type role: Optional[discord.Role]
    :param member: The member to insert into the preset
    :type member: Optional[discord.Member]
    :return: The parsed poll from the preset
    :rtype: tuple[Any, dict[Any, str]]
    """
    kwargs_reg = re.compile(r"\((member|role).?\w*\)")
    strs = [poll.prompt]
    strs.extend(poll.options)

    matches = []
    for str_ in strs:
        matches.extend(kwargs_reg.findall(str_))

    matches = set(matches)
    if ("role" in matches and not role) or ("member" in matches and not member):
        raise PollCommandError

    kwargs = {"member": member, "role": role}

    heading, *keys = [i.replace("(", "{").replace(")", "}") for i in strs]
    heading = heading.format(**kwargs)
    keys = [key.format(**kwargs) for key in keys]

    prompts = {}
    for key in [key.format(**kwargs) for key in keys]:
        prompts[key] = chr(len(prompts) + ORDINAL_A)

    return heading, prompts

class PollCommand(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="poll")
    @role_checks.config_role_check("members_role")
    async def _poll(self, ctx: commands.Context) -> None:
        """
        This is the root command for the poll group.
        This command serves no function without
        a subcommand, but will send the help message for this group.
        Essentially invokes `help poll`
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help("poll")

    @_poll.command(name="create")
    async def _poll_create(self, ctx: commands.Context, channel: Optional[discord.TextChannel], *, poll_str):
        """
        This command will let you create a new poll.
        You have two options for creating a poll. You can create a simple Y/N poll, or a poll with multiple choices.
        To create a Y/N poll, simply put your question as the `poll_str`.
        e.g `poll create Do you like Ice Cream?`
        To create a poll with multiple questions, use the following syntax. Note you are limited to 26 options.
        ```poll create {What is your favorite flavor?} [Chocolate] [Vanilla] [Strawberry]```
        The question will be the content inside the `{}` and everything inside `[]` will be the options.
        You can also mention members or roles by using the `--mention` flag:
        ```poll create {What is your favorite flavor?} [Chocolate] [Vanilla] [Strawberry] -mention member --mention role```
        `channel` The channel to send the poll message to. Will be the current channel if no other channel is supplied.
        `poll_str` The poll, following the syntax described above.
        """
        try:
            parsed_poll = await parse_poll_message(ctx, poll_str)
        except PollCommandError:
            await ctx.send(embed=embeds.ErrorEmbed("Incorrect syntax/arguments for poll to be constructed"))
            return

        channel = channel if channel else ctx.channel

        if len(parsed_poll) == 2:
            heading, mentions = parsed_poll

            message = await channel.send(" ".join(mentions),embed=embeds.InfoEmbed(heading))
            await message.add_reaction("\N{THUMBS UP SIGN}")
            await message.add_reaction("\N{THUMBS DOWN SIGN}")
        else:
            heading, opts, mentions = parsed_poll
            message = await channel.send(" ".join(mentions),
                embed=embeds.InfoEmbed(heading, description="\n".join([f"{v}: {k}" for k, v in opts.items()])))

            for emoji in opts.values():
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
    async def _poll_preset_view(self, ctx: commands.Context) -> None:
        """
        This command lets you view all the currently available presets
        """
        presets = PollPreset.objects()
        if not presets:
            await ctx.send(embed=embeds.ErrorEmbed("There are no available presets!"))
            return

        msgs = [f"Preset Name: {preset.name}\nPrompt: {preset.prompt}\nOptions:\n-" + "\n-".join(preset.options) for preset in presets]

        menu = CodeBlockMenu(msgs, "")
        await menu.start(ctx)

    @_poll_preset.command(name="load", aliases=["post"])
    async def _poll_preset_post(self, ctx: commands.Context, preset_name: str, channel: Optional[discord.TextChannel], member: Optional[discord.Member], role: Optional[discord.Role]) -> None:
        """
        This command lets you post one of the existing presets.
        If the preset message requires a member or a role, you must include that in your command.
        e.g for the preset `{(role.mention) Do you know who (member.name?) is?}`
        You must include both a `role` or a `member`
        `preset_name` The name of the preset you are loading
        `channel` The channel to send the poll message to. Will be the current channel if no other channel is supplied
        `member` The optional member, that the preset might require
        `role` The optional role, that the preset might require
        """
        preset: PollPreset = PollPreset.objects(name=preset_name).first()
        channel = channel if channel else ctx.channel

        if not preset:
            await ctx.send(embed=embeds.ErrorEmbed(
                "There is no poll preset with this name! You can create one with `poll preset save`"))
            return

        try:
            heading, opts = parse_preset(preset, role, member)
        except PollCommandError:
            await ctx.send(embed=embeds.ErrorEmbed("Incorrect arguments provided for the preset!"))
            return

        message = await channel.send(f"{heading}\n" + "\n".join([f"{v}: {k}" for k, v in opts.items()]))

        for emoji in opts.values():
            await message.add_reaction(emoji)

    @_poll_preset.command(name="save", aliases=["create"])
    async def _poll_preset_save(self, ctx: commands.Context, preset_name: str, *, poll_str) -> None:
        """
        This command lets you create a new preset.
        The presets uses the same syntax as the regular multi option polls.
        However, you will have access to a member and a role object within your preset.
        To use these presets, enclose them inside parentheses: `{Who is (member.name)?}`
        e.g to mention a role, and ask about a member, you can use the following preset:
        ```{(role.mention) what do you think about (member.name?)} [I like them!] [I hate them!] [I don't know (member.name)]```
        `preset_name`: The name of the preset you'd like to create
        `poll_str` The poll, following the syntax described above.
        """
        try:
            heading, opts, _ = await parse_poll_message(ctx, poll_str)
        except PollCommandError:
            await ctx.send(embed=embeds.ErrorEmbed("Incorrect syntax/arguments for poll to be constructed"))
            return

        try:
            PollPreset(name=preset_name, prompt=heading, options=opts.keys()).save()
        except NotUniqueError:
            await ctx.send(embed=embeds.ErrorEmbed("There is already a preset with this name!"))

        await ctx.send(embed=embeds.SuccessEmbed(f"Created a new preset: {preset_name}"))

    @_poll_preset.command(name="delete")
    @commands.has_permissions(manage_guild=True)
    async def _poll_preset_delete(self, ctx: commands.Context, preset_name: str) -> None:
        """
        This command lets you delete a current preset.
        `preset_name` The name of the preset you'd like to delete
        """
        poll: PollPreset = PollPreset.objects(name=preset_name).first()

        if not poll:
            await ctx.send(embed=embeds.ErrorEmbed("There is no poll preset with this name!"))
            return

        poll.delete()
        await ctx.send(embed=embeds.SuccessEmbed(f"Deleted the preset: {preset_name}"))

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        """
        This listener removes a poll from the current tracked events if a poll message is deleted.
        :param payload: The payload for the event
        :type payload: discord.RawMessageDeleteEvent
        """
        matched_events: List[TrackedEvent] = TrackedEvent.objects(tracking_id=payload.message_id, event_tag="poll")
        for event in matched_events:
            event.delete()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        """
        This listener removes all other reactions from poll messages in order to remove confusion.
        :param payload: The payload for the reaction add event
        :type payload: discord.RawReactionActionEvent
        """
        matched_events: List[TrackedEvent] = TrackedEvent.objects(tracking_id=payload.message_id, event_tag="poll")
        for event in matched_events:
            channel: discord.TextChannel = await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(event.tracking_id)

            for reaction in message.reactions:
                if self.bot.user not in (await reaction.users().flatten()):
                    await reaction.clear()