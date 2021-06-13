from typing import List
from discord.ext import menus, commands
from discord.utils import get
from litebot.utils import embeds
from litebot.utils.fmt_strings import CODE_BLOCK

MENU_TIMEOUT = 30.0
PREVIOUS_EMOJI = "⬆️"
NEXT_EMOJI = "⬇️"
CONFIRM_YES = "\N{WHITE HEAVY CHECK MARK}"
CONFIRM_NO = "\N{CROSS MARK}"
REMOVE_EVENT = "REACTION_REMOVE"

class ConfirmMenu(menus.Menu):
    """
    A reaction based menu to ask for confirmation.
    Do not manually call any of the methods.
    Instantiate with the prompt and then call the prompt method
    """
    def __init__(self, msg):
        super().__init__(timeout=MENU_TIMEOUT, delete_message_after=True)
        self.msg = msg
        self.result = None

    async def send_initial_message(self, ctx, channel):
        return await channel.send(embed=embeds.WarningEmbed(self.msg))

    @menus.button(CONFIRM_YES)
    async def do_confirm(self, payload):
        if payload.event_type == REMOVE_EVENT:
            return
        member = get(self.message.channel.guild.members, id=payload.user_id)
        await self.message.remove_reaction(payload.emoji, member)
        self.result = True
        self.stop()

    @menus.button(CONFIRM_NO)
    async def do_deny(self, payload):
        if payload.event_type == REMOVE_EVENT:
            return
        member = get(self.message.channel.guild.members, id=payload.user_id)
        await self.message.remove_reaction(payload.emoji, member)
        self.result = False
        self.stop()

    async def prompt(self, ctx: commands.Context) -> None:
        await self.start(ctx, wait=True)
        return self.result


class CodeBlockMenu(menus.Menu):
    """
    A reaction based menu to ask for switch between the given strings.
    Do not manually call any of the methods.
    All of the given strings will be inserted into a code block.
    Will use python syntax highlighting unless another is provided
    """
    def __init__(self, msgs: List[str], syntax: str = "py") -> None:
        super().__init__(timeout=MENU_TIMEOUT, clear_reactions_after=True)
        self.msgs = msgs
        self.syntax = syntax
        self.cur = 0

    async def send_initial_message(self, ctx, channel):
        return await channel.send(CODE_BLOCK.format(self.syntax, self.msgs[self.cur]))

    @menus.button(PREVIOUS_EMOJI)
    async def on_previous(self, payload):
        if payload.event_type == REMOVE_EVENT:
            return
        member = get(self.message.channel.guild.members, id=payload.user_id)
        await self.message.remove_reaction(payload.emoji, member)
        if self.cur != 0:
            self.cur -= 1
            await self.message.edit(content=CODE_BLOCK.format(self.syntax, self.msgs[self.cur]))

    @menus.button(NEXT_EMOJI)
    async def on_next(self, payload):
        if payload.event_type == REMOVE_EVENT:
            return
        member = get(self.message.channel.guild.members, id=payload.user_id)
        await self.message.remove_reaction(payload.emoji, member)
        if self.cur != (len(self.msgs) - 1):
            self.cur += 1
            await self.message.edit(content=CODE_BLOCK.format(self.syntax, self.msgs[self.cur]))

class DescriptionMenu(menus.Menu):
    """
    A reaction based menu to ask for switch between the given strings in the _embed description.
    Do not manually call any of the methods.
    All the given strings will be inserted into the _embed description text.
    """
    def __init__(self, msgs: List[str], title: str) -> None:
        super().__init__(timeout=MENU_TIMEOUT, clear_reactions_after=True)
        self.msgs = msgs
        self.title = title
        self.cur = 0

    async def send_initial_message(self, ctx, channel):
        return await channel.send(embed=embeds.InfoEmbed(self.title, description=self.msgs[self.cur]))

    @menus.button(PREVIOUS_EMOJI)
    async def on_previous(self, payload):
        if payload.event_type == REMOVE_EVENT:
            return
        member = get(self.message.channel.guild.members, id=payload.user_id)
        await self.message.remove_reaction(payload.emoji, member)
        if self.cur != 0:
            self.cur -= 1
            await self.message.edit(embed=embeds.InfoEmbed(self.title, description=self.msgs[self.cur]))

    @menus.button(NEXT_EMOJI)
    async def on_next(self, payload):
        if payload.event_type == REMOVE_EVENT:
            return
        member = get(self.message.channel.guild.members, id=payload.user_id)
        await self.message.remove_reaction(payload.emoji, member)
        if self.cur != (len(self.msgs) - 1):
            self.cur += 1
            await self.message.edit(embed=embeds.InfoEmbed(self.title, description=self.msgs[self.cur]))