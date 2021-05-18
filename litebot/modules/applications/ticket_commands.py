from datetime import datetime

from discord import File, Embed, PermissionOverwrite
from discord.ext import commands
from gspread import Client
from gspread.exceptions import APIError
from io import BytesIO

from litebot.core import Cog
from litebot.errors import TicketNotFound
from litebot.litebot import LiteBot
from litebot.models import Application
from litebot.modules.discord_utils.archive_command import archive_channel
from litebot.utils import embeds


class TicketCommands(Cog):
    def __init__(self, bot: LiteBot, gc: Client):
        self.bot = bot

    @commands.group(name="ticket")
    async def _ticket(self, ctx: commands.Context) -> None:
        if not ctx.invoked_subcommand:
            await ctx.send_help("ticket")

    @_ticket.command(name="accept")
    async def _ticket_accept(self, ctx: commands.Context, ign: str) -> None:
        pass

    @_ticket.command(name="deny")
    async def _ticket_deny(self, ctx: commands.Context, *, reason: str) -> None:
        ticket = Application.objects(ticket_id=ctx.channel.id).first()

        if not ticket:
            raise TicketNotFound

        for member, overwrite in ctx.channel.overwrites.items():
            if bool(overwrite.view_channel) is True:
                if member.id == self.bot.user.id or member in ctx.guild.me.roles:
                    continue

                overwrite.send_messages = False
                await ctx.channel.set_permissions(member, overwrite=overwrite)

        messages, *_ = await archive_channel(ctx.author, ctx.channel)
        transcript = ""

        for message in messages:
            transcript += f"{message.author}: {message.clean_content}\n"

        buffer = BytesIO(transcript.encode("utf8"))
        file = File(fp=buffer, filename=f"{ctx.channel.name}-transcript.txt")

        embed = embeds.ErrorEmbed("Unfortunately, your application has been denied!",
                                  description=reason, timestamp=datetime.utcnow())
        embed.set_footer(text="Attached to this message is a transcript of your application. Please download this if you'd like to keep the transcript, as this channel will be deleted.")

        await ctx.send(embed=embed)
        await ctx.send(file=file)

    @_ticket.command(name="create")
    async def _ticket_create(self, ctx: commands.Context, num: int) -> None:
        apps = self.bot.get_cog("Applications")

        try:
            answers = apps._worksheet.row_values(num + 1)
            questions = apps._worksheet.row_values(1)
            await apps._process_application(questions, answers)
        except APIError:
            await ctx.send(embed=embeds.ErrorEmbed("Sorry, the process encountered an API error, please try again!"))