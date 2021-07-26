import copy
import json
from datetime import datetime, timedelta
from io import BytesIO

import discord
from discord import TextChannel, Embed, RawReactionActionEvent, RawMessageDeleteEvent, NotFound, File
from discord.ext import tasks, commands
from gspread import service_account
from gspread.exceptions import APIError

from litebot.core import Cog
from litebot.core.context import Context
from litebot.errors import TicketNotFound
from litebot.utils.tracking_model import TrackedEvent
from litebot.utils import embeds
from litebot.utils.toggleable import Toggleable
from plugins.standard.applications.application_model import Application
from plugins.standard.applications.embeds import VoteResultsEmbed
from plugins.standard.applications.utils import TicketActions, TicketAcceptInfo

EMB_FLD_MAX = 25
FIELD_CHAR_MAX = 1024

class Applications(Cog):
    def __init__(self, creds_path, bot, plugin):
        self._config = plugin.config
        self._gc = service_account(creds_path)

        spreadsheet = self._gc.open_by_url(self._config["spreadsheet_url"])
        self._worksheet = spreadsheet.get_worksheet(0)
        self._current_applications = len(self._worksheet.get_all_values())
        self._expire_time = {k: v for k, v in self._config["vouch_expire_time"].items() if v}

        self._new_application.start()
        self.__creating_ticket = Toggleable()

    @property
    def _verify_channel(self) -> TextChannel:
        return self._bot.get_channel(self._config["verify_channel"])

    @property
    def _voting_channel(self) -> TextChannel:
        return self._bot.get_channel(self._config["voting_channel"])

    @Cog.setting(name="Create Applications",
                 description="Periodically checks the form for new responses, and processes those applications")
    @tasks.loop(seconds=10)
    async def _new_application(self):
        try:
            if len(self._worksheet.get_all_values()) > self._current_applications:
                self._bot.logger.info("New application has been recieved!")

                questions = self._worksheet.row_values(1)
                answers = self._worksheet.row_values(self._current_applications + 1)
                await self._process_application(questions, answers)
        except APIError:
            self._bot.logger.error("Applications encountered an API error!")

    @Cog.setting(name="Ticket Commands",
                 description="Manage tickets created from applications!",
                 config={"auto_vote": False, "auto_vote_preset": "", "auto_vote_mention_role": 0})
    @commands.group(name="ticket")
    async def _ticket(self, ctx: Context):
        """
        Root command for the ticket group
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help("ticket")

    @_ticket.command(name="create")
    async def _ticket_create(self, ctx: Context, num: int):
        """
        Create a new ticket
        **Args**:
            `num`: The application number to create the ticket for
        """
        try:
            questions = self._worksheet.row_values(1)
            answers = self._worksheet.row_values(num + 1)
            await self._process_application(questions, answers)
        except APIError:
            await ctx.send(embed=embeds.ErrorEmbed("Sorry, the process encountered an API error, please try again!"))

    @_ticket.command(name="deny")
    async def _ticket_deny(self, ctx: Context, *, reason):
        """
        Deny a ticket
        **Args**:
            `reason`: The reason the ticket was denied
        """
        ticket: Application = Application.objects(ticket_id=ctx.channel.id).first()

        if not ticket:
            raise TicketNotFound

        for member, overwrite in ctx.channel.overwrites.items():
            if bool(overwrite.view_channel) is True:
                if member.id == self._bot.user.id or member in ctx.guild.me.roles:
                    continue

                overwrite.send_messages = False
                await ctx.channel.set_permissions(member, overwrite=overwrite)

        embed = embeds.ErrorEmbed("Unfortunately, your application has been denied!", description=reason,
                                  timestamp=datetime.utcnow())

        # try to disable the votes for the voting message
        try:
            voting_message = await self._voting_channel.fetch_message(ticket.voting_message_id)
            reactions = {r.emoji: (r.count - 1) for r in voting_message.reactions if r.me}
            await voting_message.edit(embed=VoteResultsEmbed(TicketActions.DENY, ticket, self._config, reactions))
            await voting_message.clear_reactions()
        except:
            pass # well, we tried

        if not self._bot.get_cog("ArchiveCommand"):
            return await ctx.send(embed=embed)

        #TODO: Make this not require imports
        from plugins.standard.discord_utils.archives.utils import archive_channel

        messages, *_ = await archive_channel(ctx.author, ctx.channel)
        transcript = "".join((f"{message.author}: {message.clean_content}\n" for message in messages))

        embed.set_footer(text="Attached to this message is a transcript of your application. "
                              "Please download this if you'd like to keep the transcript, "
                              "as this channel will be deleted.")

        await ctx.send(embed=embed, file=File(fp=BytesIO(transcript.encode("utf8")),
                                              filename=f"{ctx.channel.name}-transcript.txt"))

    @_ticket.command(name="accept")
    async def _ticket_accept(self, ctx: Context, member: discord.Member, *, accept: TicketAcceptInfo):
        """
        Accept a ticket
        **Args**:
            `member`: The member that the ticket is for
            `accept`: Extra flags for the command:
                `--whitelist|-w <ign>` The username to whitelist on all servers
                `--timezone|-tz <timezone>` Set the member's timezone
        """
        ticket: Application = Application.objects(ticket_id=ctx.channel.id).first()

        if not ticket:
            raise TicketNotFound

        for member_, overwrite in ctx.channel.overwrites.items():
            if bool(overwrite.view_channel) is True:
                if member_.id == self._bot.user.id or member_ in ctx.guild.me.roles:
                    continue

                overwrite.send_messages = False
                await ctx.channel.set_permissions(member_, overwrite=overwrite)

        #TODO: Better way for dynamic command functionality
        if accept.whitelist and ctx.bot.get_command("whitelist add"):
            await ctx.bot.get_command("whitelist add")(ctx, accept.whitelist)

        if accept.timezone and ctx.bot.get_command("timezone set"):
            msg = copy.copy(ctx.message)
            msg.author = member
            msg.content = ctx.prefix + f"timezone set {accept.timezone}"

            new_ctx = await self._bot.get_context(msg, cls=type(ctx))
            await ctx.bot.get_command("timezone set")(new_ctx, "US/Eastern")

        # try to disable the votes for the voting message
        try:
            voting_message = await self._voting_channel.fetch_message(ticket.voting_message_id)
            reactions = {r.emoji: (r.count - 1) for r in voting_message.reactions if r.me}
            await voting_message.edit(embed=VoteResultsEmbed(TicketActions.ACCEPT, ticket, self._config, reactions))
            await voting_message.clear_reactions()
        except:
            pass # well, we tried

        embed = embeds.SuccessEmbed("Congratulations on your acceptance!", timestamp=datetime.utcnow())

        if not self._bot.get_cog("ArchiveCommand"):
            return await ctx.send(embed=embed)

        from plugins.standard.discord_utils.archives.utils import archive_channel

        messages, *_ = await archive_channel(ctx.author, ctx.channel)
        transcript = "".join((f"{message.author}: {message.clean_content}\n" for message in messages))

        buffer = BytesIO(transcript.encode("utf8"))
        file = File(fp=buffer, filename=f"{ctx.channel.name}-transcript.txt")

        embed.set_footer(text="Attached to this message is a transcript of your application. "
                              "Please download this if you'd like to keep the transcript, "
                              "as this channel will be deleted.")
        await ctx.send(embed=embed, file=file)

    async def _process_application(self, questions: tuple[str], answers: tuple[str]) -> None:
        application = {k : v for k, v in dict(zip(questions, answers)).items() if v}

        name = application[self._config["discord_name_question"]]
        embed_list = self._generate_embeds(name, application)

        ap_db = Application(name=name, application=json.dumps(application), application_embeds=[e.to_dict() for e in embed_list]).save()

        if not self._config["required_vouches"]:
            with self.__creating_ticket:
                await self._create_ticket(ap_db)
        else:
            confirm_message = await self._verify_channel.send(embed=embed_list[0])
            await confirm_message.add_reaction(self._config["vote_yes_emoji"])

            TrackedEvent(
                tracking_id=confirm_message.id,
                event_tag="app_vouch",
                expire_time=datetime.utcnow() + timedelta(**self._expire_time),
                extra_info={
                    "name": name,
                    "application": json.dumps(application),
                    "application_embeds": [e.to_dict() for e in embed_list]
                }
            ).save()

        self._current_applications += 1

    async def _create_ticket(self, application: Application, voucher=None):
        channel: TextChannel = await (await self._bot.guild()).create_text_channel(
            name=f"{application.name.split('#')[0]} application",
            category=await self._bot.fetch_channel(self._config["applications_category"])
        )

        app_embeds = [Embed.from_dict(d) for d in application.application_embeds]
        messages = [await channel.send(embed=embed) for embed in app_embeds]
        await messages[-1].pin()

        voting_message = await self._voting_channel.send(
            embed=embeds.InfoEmbed(f"Vote for {application.name.split('#')[0]}")
        )

        application.update(ticket_id=channel.id, voting_message_id=voting_message.id)

        await voting_message.add_reaction(self._config["vote_yes_emoji"])
        await voting_message.add_reaction(self._config["vote_no_emoji"])

        try:
            name, discriminator, *_ = application.name.split("#")
            applicant = list(
                filter(lambda m: m.name == name and m.discriminator == discriminator, (await self._bot.guild()).members)
            )[0]
            vouch_str = f"Your application has been vouched by {voucher.mention}\nWe will be with you shortly" if \
                voucher else ""

            await channel.set_permissions(applicant, read_messages=True, send_messages=True, attach_files=True)
            await channel.send(
                f"Thank you for applying {applicant.mention}! " + vouch_str)
            application.update(applicant_id=applicant.id)
        except IndexError:
            vouch_str = f"Application vouched by {voucher.mention}" if voucher else ""
            await channel.send(f"Applicant applied with an invalid discord name, or have left the server. " + vouch_str)

    @Cog.listener(type=Cog.ListenerTypes.DISCORD, name="on_raw_reaction_add")
    async def _ticket_vouch(self, payload: RawReactionActionEvent):
        matched_event: TrackedEvent = TrackedEvent.objects(tracking_id=payload.message_id, event_tag="app_vouch").first()

        if not matched_event or payload.user_id == self._bot.user.id:
            return

        application = Application.objects(**matched_event.extra_info).first()
        message = await self._verify_channel.fetch_message(payload.message_id)
        reaction = list(filter(lambda r: r.me, message.reactions))

        if reaction and (reaction[0].count - 1) >= self._config["required_vouches"]:
            with self.__creating_ticket:
                await self._create_ticket(application, await self._bot.fetch_user(payload.user_id))
                await message.delete()
                matched_event.delete()

    @Cog.listener(type=Cog.ListenerTypes.DISCORD, name="on_raw_message_delete")
    async def _ticket_delete_safety(self, payload: RawMessageDeleteEvent):
        matched_event: TrackedEvent = TrackedEvent.objects(tracking_id=payload.message_id, event_tag="app_vouch").first()

        if not matched_event or self.__creating_ticket:
            return

        application = Application.objects(**matched_event.extra_info).first()
        application_embeds = [Embed.from_dict(d) for d in application.application_embeds]
        confirmation_message = await self._verify_channel.send(embed=application_embeds[0])

        await confirmation_message.add_reaction(self._config["vote_yes_emoji"])
        matched_event.update(tracking_id=confirmation_message.id)

    @Cog.listener(type=Cog.ListenerTypes.DISCORD)
    async def on_app_vouch_expire(self, event):
        try:
            message = await self._verify_channel.fetch_message(event.tracking_id)
            with self.__creating_ticket:
                await message.delete()
            event.delete()
        except NotFound:
            event.delete()

    @_new_application.before_loop
    async def _before_new_application(self) -> None:
        await self._bot.wait_until_ready()

    def _generate_embeds(self, name: str, application: dict[str, str]) -> list[embeds.InfoEmbed]:
        embed_list = []
        if len(application) > EMB_FLD_MAX:
            original_app = application
            application = {v: application[v] for i, v in enumerate(application) if i <= EMB_FLD_MAX}
            embed_list.extend(
                self._generate_embeds(name, {v: original_app[v] for i, v in enumerate(original_app) if i > EMB_FLD_MAX}))

        embed_list.append(self._generate_embed(name, application))
        return embed_list[::-1]

    def _generate_embed(self, name: str, application: dict[str, str]) -> embeds.InfoEmbed:
        new_embed = embeds.InfoEmbed(f"{name.split('#')[0]} Application")
        for q, a in application.items():
            if len(a) <= FIELD_CHAR_MAX:
                new_embed.add_field(name=q, value=a, inline=False)
            else:
                answer_parts = [a[i:i + FIELD_CHAR_MAX] for i in range(0, len(a), FIELD_CHAR_MAX)]
                for num, part in enumerate(answer_parts):
                    if num == 0:
                        new_embed.add_field(name=q, value=part, inline=False)
                    else:
                        new_embed.add_field(name="^ Extended", value=part, inline=False)
        return new_embed
