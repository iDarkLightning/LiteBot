import re
import discord
from typing import Union, Tuple
from discord.ext import commands

from litebot.utils import embeds


def parse_poll_message(message: str) -> Union[str, Tuple[str, dict]]:
    poll_reg = re.compile(r"[{\[][\w\s?]+[}\]]")
    matches = poll_reg.findall(message)

    if not len(matches):
        return message

    question = ""
    prompts = {}

    for match in matches:
        if re.match("{[\w\s?]+}", match) and not question:
            question = re.sub("[{}]+", "", match)
        elif re.match("\[[\w\s?]+]", match) and len(prompts) < 27:
            prompts[(re.sub("[\[\]]+", "", match))] = chr(len(prompts) + 127462)

    return question, prompts


class PollCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="poll")
    async def _poll(self, ctx: commands.Context) -> None:
        if not ctx.invoked_subcommand:
            await ctx.send_help("poll")

    @_poll.command(name="create")
    async def _poll_create(self, ctx: commands.Context, channel: discord.TextChannel, *, poll_str):
        parsed_poll = parse_poll_message(poll_str)
        if isinstance(parsed_poll, str):
            message = await channel.send(embed=embeds.InfoEmbed(parsed_poll))
            await message.add_reaction("\N{THUMBS UP SIGN}")
            await message.add_reaction("\N{THUMBS DOWN SIGN}")
        else:
            heading, opts = parsed_poll
            message = await channel.send(
                embed=embeds.InfoEmbed(heading, description="\n".join([f"{v}: {k}" for k, v in opts.items()])))

            for emoji in opts.values():
                await message.add_reaction(emoji)
