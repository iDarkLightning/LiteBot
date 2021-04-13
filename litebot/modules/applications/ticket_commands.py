from discord.ext import commands
from gspread import Client

from litebot.errors import TicketNotFound
from litebot.litebot import LiteBot
from litebot.models import Application


class TicketCommands(commands.Cog):
    def __init__(self, bot: LiteBot, gc: Client):
        self.bot = bot
        self.gc = gc

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
        pass

    async def cog_before_invoke(self, ctx):
        ticket = Application.objects(ticket_id=ctx.channel.id).first()

        if ctx.invoked_subcommand != "create" and not ticket:
            raise TicketNotFound

        ctx.ticket = ticket