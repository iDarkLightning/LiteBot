import argparse
import shlex

from discord.ext.commands import Converter


class TicketAcceptInfo(Converter):
    def __init__(self, *, whitelist=None, timezone=None, vote="2w", roles=None):
        self.whitelist = whitelist
        self.timezone = timezone
        self.vote = vote
        self.roles = roles

    async def convert(self, ctx, argument):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--whitelist", "-w")
        parser.add_argument("--vote", "-v")
        parser.add_argument("--timezone", "-tz")
        parser.add_argument("--roles", "-r", nargs="*")

        parsed = parser.parse_args(shlex.split(argument))

        kwargs = {"vote": parsed.vote, "roles": parsed.roles}

        if ctx.bot.get_command("whitelist add"):
            kwargs["whitelist"] = parsed.whitelist

        if ctx.bot.get_command("timezone set"):
            kwargs["timezone"] = parsed.timezone

        return TicketAcceptInfo(**kwargs)

class TicketActions:
    ACCEPT = "Accepted"
    DENY = "Denied"