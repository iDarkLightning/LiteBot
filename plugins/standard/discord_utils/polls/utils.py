import shlex, argparse
from discord.ext.commands import MemberConverter, RoleConverter, MemberNotFound, RoleNotFound, Converter

from plugins.standard.discord_utils.polls.errors import PollCommandError
from plugins.standard.discord_utils.polls.poll_preset_model import PollPreset

ORDINAL_A = 127462


class Poll(Converter):
    def __init__(self, name=None, prompt=None, options=None, mentions=None):
        self.name = name
        self.prompt = prompt
        self.options = options or {}
        self.mentions = mentions
        self.formatted_options = "\n".join([f"{v}: {k}" for k, v in self.options.items()])

    async def convert(self, ctx, argument):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--prompt", "-p", nargs="*")
        parser.add_argument("--name", "-n", nargs="*")
        parser.add_argument("--option", "-o", action="append", nargs="+", dest="options")
        parser.add_argument("--mention", "-m", action="append", nargs="*", dest="mentions")

        poll = parser.parse_args(shlex.split(argument))

        if not poll.prompt:
            raise PollCommandError("Your poll is missing a prompt!")

        prompt = " ".join(poll.prompt)
        mentions = " ".join([m.mention for m in [await role_or_member(ctx, i) for i in [" ".join(
            j) for j in poll.mentions or []]] if m])
        opts = {" ".join(v): chr(i + ORDINAL_A) for i, v in enumerate(poll.options[:26])}

        return Poll(" ".join(poll.name or []), prompt, opts, mentions)

class PollPresetConverter(Converter):
    async def convert(self, ctx, argument):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--name", "-n", nargs="*")
        parser.add_argument("--member", "-m", nargs="*")
        parser.add_argument("--role", "-r", nargs="*")

        poll = parser.parse_args(shlex.split(argument))
        preset: PollPreset = PollPreset.objects(name=" ".join(poll.name)).first()

        if not preset:
            raise PollCommandError("No preset found with that name!")

        member = await role_or_member(ctx, " ".join(poll.member or []))
        role = await role_or_member(ctx, " ".join(poll.role or []))

        prompt = preset.prompt.format(member=member, role=role)
        options = {v: chr(i + ORDINAL_A) for i, v in enumerate(preset.options[:26])}

        return Poll(poll.name, prompt, options)

async def role_or_member(ctx, arg):
    try:
        return await MemberConverter().convert(ctx, arg)
    except MemberNotFound:
        try:
            return await RoleConverter().convert(ctx, arg)
        except RoleNotFound:
            return None
