from typing import Optional

import discord
from discord.ext import commands

from litebot.core import Cog, Context
from litebot.models import TrackedEvent
from litebot.utils import embeds
from litebot.utils.menus import ConfirmMenu, CONFIRM_YES
from plugins.standard.archives.archived_channel_model import ArchivedChannel
from plugins.standard.archives.utils import archive_channel



class ArchiveCommand(Cog):
    @Cog.setting(name="Archive Channel", description="Archive a discord channel to the database")
    @commands.command(name="archive")
    async def _archive(self, ctx: Context, channel: Optional[discord.TextChannel]):
        channel = channel or ctx.channel
        matched_archive = ArchivedChannel.objects(channel_id=channel.id).first()

        if matched_archive:
            if not await ConfirmMenu(
                "There is already a channel with this ID in the archives. Would you like to override it?").prompt(ctx):
                return await ctx.send(embed=embeds.ErrorEmbed("Aborted"))
            matched_archive.delete()

        if not await ConfirmMenu("Are you sure you would like to archive this channel?").prompt(ctx):
            return await ctx.send(embed=embeds.ErrorEmbed("Aborted"))

        for target in filter(lambda s: self._filter_targets(ctx.guild, s), channel.overwrites):
            if target.name not in [self._bot]:
                await channel.set_permissions(target, overwrite=None)

        async with channel.typing():
            message = await channel.send(embed=embeds.InfoEmbed("Archiving Channel..."))
            await archive_channel(ctx.author, channel)
            await message.edit(embed=embeds.InfoEmbed("Channel Archived!"))

        message = await self._bot.log_channel.send(embed=embeds.InfoEmbed(f"Please confirm the deletion of {channel.name}"))
        TrackedEvent(tracking_id=message.id, event_tag="archive", extra_info={"deletion_channel": channel.id}).save()
        await message.add_reaction(CONFIRM_YES)

    @Cog.listener(type=Cog.ListenerTypes.DISCORD)
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        matched_event = TrackedEvent.objects(tracking_id=payload.message_id, event_tag="archive").first()
        if payload.user_id == self._bot.user.id or not matched_event:
            return

        channel = self._bot.get_channel(matched_event.extra_info["deletion_channel"])
        message = await self._bot.log_channel.fetch_message(payload.message_id)
        await channel.delete()
        await message.delete()
        matched_event.delete()

    def _filter_targets(self, guild, target):
        if isinstance(target, discord.Member):
            return target.id != self._bot.user.id
        else:
            return target not in guild.me.roles