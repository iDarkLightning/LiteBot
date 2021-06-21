from datetime import datetime
from typing import Any, Type
import discord

from plugins.standard.discord_utils.archives.archived_channel_model import ArchivedChannel


async def archive_channel(archiver: discord.Member, channel: discord.TextChannel) -> tuple[Any, Type[ArchivedChannel]]:
    messages = await channel.history(limit=None, oldest_first=True).flatten()

    ArchivedChannel(archiver=_member_to_dict(archiver), pins=[_message_to_dict(m) for m in (await channel.pins())],
                    created_time=datetime.utcnow(), channel_id=channel.id, name=channel.name, topic=channel.topic,
                    category=channel.category.name, messages=[_message_to_dict(m) for m in messages],
                    users=[_member_to_dict(m) for m in channel.members]).save()

    return messages, ArchivedChannel


def _attachment_to_dict(attachment: discord.Attachment):
    return {
        "content_type": attachment.content_type,
        "filename": attachment.filename,
        "url": attachment.url,
        "proxy_url": attachment.proxy_url
    }

def _message_to_dict(message: discord.Message):
    return {
        "attachments": [_attachment_to_dict(a) for a in message.attachments],
        "author": _member_to_dict(message.author),
        "channel": message.channel.id,
        "clean_content": message.clean_content,
        "content": message.content,
        "created_at": message.created_at,
        "created_at_str": message.created_at.strftime("%d/%m/%y"),
        "_embeds": [e.to_dict() for e in message.embeds],
        "id": message.id,
        "jump_url": message.jump_url
    }

def _member_to_dict(member: discord.Member):
    return {
        "name": member.name,
        "avatar": str(member.avatar_url),
        "color": member.color.value,
        "id": member.id,
        "display_name": member.display_name,
    }