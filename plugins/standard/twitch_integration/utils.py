import discord

from litebot.core.minecraft import ServerCommandContext
from litebot.core.minecraft.commands.arguments import Suggester, StrictSuggester


class ConnectedChannelSuggester(StrictSuggester):
    """
    A strict suggester for the /stream disconnect command.
    Suggests the channels that the player is currently connected to, and ensures that they do not attempt to
    disconnect from a channel that they aren't connected to.
    """
    async def suggest(self, ctx: ServerCommandContext, arg: str, prior_args: dict) -> list:
        chat_cog = ctx.bot.get_cog("TwitchChat")
        to_suggest = []

        for channel in chat_cog.channels:
            connections = chat_cog.connections[channel]
            if ctx.player.uuid in [c.player.uuid for c in connections]:
                to_suggest.append(channel)

        return to_suggest


class ChannelSuggester(Suggester):
    """
    A suggester for the /stream connect command.
    Suggests channels that other members on the server are currently connected to, or the channel of any members who
    might be currently streaming on twitch.
    """
    async def suggest(self, ctx: ServerCommandContext, arg: str, prior_args: dict) -> list:
        chat_cog = ctx.bot.get_cog("TwitchChat")
        guild = await ctx.bot.guild()
        streams = list(filter(lambda n: n is not None,map(
            self.get_stream_name, filter(lambda m: any([isinstance(a, discord.Streaming) for a in m.activities]),
                           sum([role.members for role in [guild.get_role(r) for r in ctx.bot.config["members_role"]]],
                               [])))))

        streams.extend(chat_cog.channels.keys())
        current_connections = []

        for channel in chat_cog.channels:
            connections = chat_cog.connections[channel]
            if ctx.player.uuid in [c.player.uuid for c in connections]:
                current_connections.append(channel)

        return list(set([s for s in streams if s not in current_connections]))

    def get_stream_name(self, member: discord.Member):
        streaming_activity = list(filter(lambda a: isinstance(a, discord.Streaming), member.activities))[0]

        if streaming_activity.platform == "Twitch":
            return streaming_activity.twitch_name