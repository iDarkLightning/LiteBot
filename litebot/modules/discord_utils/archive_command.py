import discord
from typing import Optional, Any, Type

from discord import Message, Member, Attachment
from discord.ext import commands

from litebot.core import Cog
from litebot.errors import ConfirmationDenied
from litebot.litebot import LiteBot
from litebot.models import TrackedEvent
from litebot.models.archived_channel_model import ArchivedChannel
from litebot.utils import embeds
from litebot.utils.menus import ConfirmMenu, CONFIRM_YES


def _attachment_to_dict(attachment: Attachment):
    return {
        "content_type": attachment.content_type,
        "filename": attachment.filename,
        "url": attachment.url,
        "proxy_url": attachment.proxy_url
    }

def _message_to_dict(message: Message):
    return {
        "attachments": [_attachment_to_dict(a) for a in message.attachments],
        "author": _member_to_dict(message.author),
        "channel": message.channel.id,
        "clean_content": message.clean_content,
        "content": message.content,
        "created_at": message.created_at,
        "created_at_str": message.created_at.strftime("%d/%m/%y"),
        "embeds": [e.to_dict() for e in message.embeds],
        "id": message.id,
        "jump_url": message.jump_url
    }

def _member_to_dict(member: Member):
    return {
        "name": member.name,
        "avatar": str(member.avatar_url),
        "color": member.color.value,
        "id": member.id,
        "display_name": member.display_name,
    }

async def archive_channel(archiver: Member, channel: discord.TextChannel) -> tuple[Any, Type[ArchivedChannel]]:
    messages = await channel.history(limit=None, oldest_first=True).flatten()

    ArchivedChannel(archiver=_member_to_dict(archiver), pins=[_message_to_dict(m) for m in (await channel.pins())],
                    channel_id=channel.id, name=channel.name, topic=channel.topic,
                    category=channel.category.name, messages=[_message_to_dict(m) for m in messages],
                    users=[_member_to_dict(m) for m in channel.members]).save()

    return messages, ArchivedChannel

class ArchiveCommand(Cog):
    def __init__(self, bot: LiteBot):
        self.bot = bot

    @commands.command(name="archive")
    async def _archive(self, ctx: commands.Context, channel: Optional[discord.TextChannel]):
        channel = channel if channel else ctx.channel
        matched_archive = ArchivedChannel.objects(channel_id=channel.id).first()

        if matched_archive:
            override = await ConfirmMenu(
                "There is already a channel with this ID in the archives. Would you like to override it?").prompt(ctx)

            if not override:
                raise ConfirmationDenied
            matched_archive.delete()

        confirmation = await ConfirmMenu("Are you sure you would like to archive this channel?").prompt(ctx)
        if not confirmation:
            raise ConfirmationDenied

        for target in filter(lambda s: self._filter_targets(ctx.guild, s), channel.overwrites):
            if target.name not in [self.bot]:
                await channel.set_permissions(target, overwrite=None)

        async with channel.typing():
            message = await channel.send(embed=embeds.InfoEmbed("Archiving Channel..."))
            await archive_channel(ctx.author, channel)
            await message.edit(embed=embeds.InfoEmbed("Channel Archived!"))

        message = await self.bot.log_channel.send(embed=embeds.InfoEmbed(f"Please confirm the deletion of {channel.name}"))
        TrackedEvent(tracking_id=message.id, event_tag="archive", extra_info={"deletion_channel": channel.id}).save()
        await message.add_reaction(CONFIRM_YES)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        matched_event = TrackedEvent.objects(tracking_id=payload.message_id, event_tag="archive").first()
        if payload.user_id == self.bot.user.id or not matched_event:
            return

        channel = self.bot.get_channel(matched_event.extra_info["deletion_channel"])
        message = await self.bot.log_channel.fetch_message(payload.message_id)
        await channel.delete()
        await message.delete()
        matched_event.delete()

    def _filter_targets(self, guild, target):
        if isinstance(target, discord.Member):
            return target.id != self.bot.user.id
        else:
            return target not in guild.me.roles

