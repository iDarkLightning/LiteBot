from discord.ext import commands
from gspread import Client
from gspread.exceptions import APIError

from litebot.core import Cog
from litebot.errors import TicketNotFound
from litebot.litebot import LiteBot
from litebot.models import Application
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
    async def _ticket_deny(self, ctx: commands.Context, ign: str) -> None:
        pass

    @_ticket.command(name="create")
    async def _ticket_create(self, ctx: commands.Context, num: int) -> None:
        apps = self.bot.get_cog("Applications")

        try:
            answers = apps._worksheets.row_values(num + 1)
            questions = apps._worksheets.row_values(1)
            await apps._process_application(questions, answers)
        except APIError:
            await ctx.send(embed=embeds.ErrorEmbed("Sorry, the process encountered an API error, please try again!"))

    async def cog_before_invoke(self, ctx):
        ticket = Application.objects(ticket_id=ctx.channel.id).first()

        if ctx.invoked_subcommand != "create" and not ticket:
            raise TicketNotFound

        ctx.ticket = ticket