from typing import Optional
import discord
from discord.ext import commands, tasks
from discord.utils import get

from litebot.core import Cog
from litebot.litebot import LiteBot
from litebot.utils import embeds
import datetime
from datetime import datetime
from litebot.utils.data_manip import parse_reason, reason_datetime_parser


class ModeratorCommands(Cog):
    def __init__(self, bot: LiteBot, module):
        self.bot = bot
        self.config = self.bot.module_config[module]["config"]
        self._revoke_checks.start()


    async def _mute_role(self) -> discord.Role:
        """
        The mute role
        """
        return get((await self.bot.guild()).roles, id=self.config["mute_role_id"])

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Prepares the mute role, and sets its perms
        """
        for channel in (await self.bot.guild()).channels:
            try:
                await channel.set_permissions((await self._mute_role()), send_messages=False, connect=False)
            except discord.Forbidden:
                pass

    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def _clear(self, ctx: commands.Context, amount: Optional[int] = 5) -> None:
        """
        Deletes the the given amount of messages in the channel.
        If no amount is given, it will default to 5.
        `amount`: The amount of messages to delete
        """
        await ctx.channel.purge(limit=amount + 1)

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def _kick(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None) -> None:
        """
        Kicks a member. They will be able to rejoin with an invite link.
        `member` The member you are kicking
        `reason` The reason for kicking, this is optional
        """
        reason = f"{reason} [{datetime.utcnow()}] [{ctx.author.id}]"

        await member.kick(reason=reason)
        log_channel = await self.bot.log_channel
        log_embed = embeds.ModeratorLogEmbed(embeds.ModeratorActions.KICK, reason, ctx.author, member)
        await log_channel.send(embed=log_embed)
        self.bot.logger.info(f"{ctx.author} kicked {member.name}. Info: {reason}")

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def _ban(self, ctx: commands.Context, member: discord.Member, *args) -> None:
        """
        Bans a member. You can specify a time after which the ban will be revoked.
        The time will be the last statement in your args.
        Time format: 1w3d4h6m30s -> 1 Week, 3 Days, 4 Hours, 6 Minutes, 30 Seconds from current time.
        You do not need to include all of those, `3m30s` will work just fine.
        `member` The member you are banning
        `reason` The reason for banning, this is optional. The last phrase here will be the time. Ex: `Was rude 2w`
        """
        reason = parse_reason(ctx.author, args)

        await member.ban(reason=reason)
        log_channel = await self.bot.log_channel
        log_embed = embeds.ModeratorLogEmbed(embeds.ModeratorActions.BAN, reason, ctx.author, member)
        await log_channel.send(embed=log_embed)
        self.bot.logger.info(f"{ctx.author} banned {member.name}. Info: {reason}")

    @commands.group(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def _mute(self, ctx: commands.Context) -> None:
        """
        This is the root command for the mute group.
        This command serves no function without
        a subcommand, but will send the help message for this group.
        Essentially invokes `help mute`
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help("mute")

    @_mute.command(name="add")
    async def _mute_add(self, ctx: commands.Context, member: discord.Member, *args) -> None:
        """
        Mutes a member. You can specify a time after which the mute will be revoked.
        The time will be the last statement in your args.
        Time format: 1w3d4h6m30s -> 1 Week, 3 Days, 4 Hours, 6 Minutes, 30 Seconds from current time.
        You do not need to include all of those, `3m30s` will work just fine.
        `member` The member you are muting
        `reason` The reason for muting, this is optional. The last phrase here will be the time. Ex: `Was rude 2w`
        """
        reason = parse_reason(ctx.author, args)

        mute_role = await self._mute_role()

        log_channel = await self.bot.log_channel
        await member.add_roles(mute_role, reason=reason)
        log_embed = embeds.ModeratorLogEmbed(embeds.ModeratorActions.MUTE, reason, ctx.author, member)
        await log_channel.send(embed=log_embed)
        self.bot.logger.info(f"{ctx.author} muted {member.name}. Info: {reason}")

    @_mute.command(name="revoke")
    async def _mute_revoke(self, ctx:commands.Context, member: discord.Member):
        """
        Revokes a mute.
        `member` The member you are pardoning
        """
        mute_role = await self._mute_role()

        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            log_channel = await self.bot.log_channel
            log_embed = embeds.ModeratorLogEmbed(embeds.ModeratorActions.PARDON, "Revoked Mute", ctx.author, member)
            await log_channel.send(embed=log_embed)
        else:
            await ctx.send(embed=embeds.ErrorEmbed("That user is not muted"))

    @tasks.loop(seconds=60.0)
    async def _revoke_checks(self) -> None:
        """
        Checks every 60 seconds if any ban/mute time has expired.
        If the time has expired, the user is pardoned
        """
        guild = await self.bot.guild()
        for ban in await guild.bans():
            parsed_time = reason_datetime_parser(ban.reason)
            if isinstance(parsed_time, datetime) and datetime.utcnow().time() >= parsed_time.time():
                await self._handle_revoke_ban(ban.user)

        mute_role = await self._mute_role()
        members = filter(lambda m: mute_role in m.roles, guild.members)

        for member in members:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.member_role_update, user=guild.me):
                if entry.target != member:
                    continue

                if mute_role in entry.changes.after.roles:
                    parsed_time = reason_datetime_parser(entry.reason)
                    if isinstance(parsed_time, datetime) and datetime.utcnow().time() >= parsed_time.time():
                        await self._handle_revoke_mute(entry.target)
                    else:
                        break

    async def _handle_revoke_ban(self, user: discord.User) -> None:
        """
        Revokes a user's ban
        :param user: The user who's ban is being removed
        :type user: discord.User
        """
        guild = await self.bot.guild()
        await guild.unban(user, reason="The user's ban time is over")
        log_channel = await self.bot.log_channel
        log_embed = embeds.ModeratorLogEmbed(embeds.ModeratorActions.PARDON, "Revoked Ban: Time Expired",
                                             self.bot.user, user)
        await log_channel.send(embed=log_embed)
        self.bot.logger.info(f"{user}'s ban has been revoked. Info: Time Expired")


    async def _handle_revoke_mute(self, member: discord.Member) -> None:
        """
        Revokes a user's mute
        :param member: The member who's mute we are revoking
        :type member: discord.Member
        """
        mute_role = await self._mute_role()

        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            log_channel = await self.bot.log_channel
            log_embed = embeds.ModeratorLogEmbed(embeds.ModeratorActions.PARDON, "Revoked Mute: Time Expired",
                                                 self.bot.user, member)
            await log_channel.send(embed=log_embed)
            self.bot.logger.info(f"{member}'s mute has been revoked. Info: Time Expired")