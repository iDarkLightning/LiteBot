from datetime import datetime, timedelta
from typing import Tuple, List

from discord import RawReactionActionEvent, TextChannel, Embed, RawMessageDeleteEvent, NotFound, User, HTTPException
from discord.ext import commands, tasks
from gspread import Client
from gspread.exceptions import APIError

from litebot.core import Cog
from litebot.litebot import LiteBot
from litebot.models import TrackedEvent, Application
from litebot.utils import embeds
from litebot.utils.menus import CONFIRM_YES
from litebot.utils.misc import Toggleable

EMBED_FIELD_MAX = 25
FIELD_CHAR_MAX = 1024
YES_EMOJI = "<:yes:760951181283033128>"
NO_EMOJI = "<:no:816732205526155316>"
CHECK_EMOJI = "☑️"
CROSS_EMOJI = "❌"


class Applications(Cog):
    def __init__(self, bot: LiteBot, gc: Client):
        self.bot = bot
        self._config = self.bot.module_config["applications"]["config"]
        self._gc = gc

        spreadsheet = self._gc.open_by_url(self._config["spreadsheet_url"])
        self._worksheet = spreadsheet.get_worksheet(0)
        self._current_applications = len(self._worksheet.get_all_values())
        self._expire_time = {k: v for k, v in self._config["vouch_expire_time"].items() if v}
        self._new_application.start()
        self._vouch_expire.start()
        self._creating_ticket = Toggleable()

    @property
    def _verify_channel(self) -> TextChannel:
        """
        The channel to send the applications to be verified before a ticket is created.
        :return: The channel object
        :rtype: TextChannel
        """
        return self.bot.get_channel(self._config["verify_channel"])

    @property
    def _voting_channel(self) -> TextChannel:
        """
        The channel in which to send the votes for the applicants
        :return: The channel object
        :rtype: TextChannel
        """
        return self.bot.get_channel(self._config["voting_channel"])

    @tasks.loop(seconds=10)
    async def _new_application(self) -> None:
        """
        A background task to check if a new application has been created.
        Processes the new application if there is a new one.
        """
        try:
            if len(self._worksheet.get_all_values()) > self._current_applications:
                self.bot.logger.info("New application has been recieved!")

                questions = self._worksheet.row_values(1)
                answers = self._worksheet.row_values(self._current_applications + 1)
                await self._process_application(questions, answers)
        except APIError:
            self.bot.logger.error("Applications encountered an API error!")

    @tasks.loop(seconds=60)
    async def _vouch_expire(self) -> None:
        """
        Deletes all current verify messages that have expired
        """
        events = [e for e in TrackedEvent.objects(event_tag="application") if
                  datetime.utcnow().time() >= e.expire_time.time()]
        for event in events:
            try:
                message = await self._verify_channel.fetch_message(event.tracking_id)
                with self._creating_ticket:
                    await message.delete()
                event.delete()
            except NotFound:
                event.delete()

    @_new_application.before_loop
    async def _before_new_application(self) -> None:
        """
        Ensures that the bot is ready before starting `_new_application`
        """
        await self.bot.wait_until_ready()

    @_vouch_expire.before_loop
    async def _before_vouch_expire(self) -> None:
        """
        Ensures that the bot is ready before starting `_vouch_expire`
        """
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        """
        Creates the ticket if a reaction is added to a verify message
        :param payload: The payload for the event
        :type payload: RawReactionActionEvent
        """
        matched_event: TrackedEvent = TrackedEvent.objects(tracking_id=payload.message_id,
                                                           event_tag="application").first()
        if not matched_event or payload.user_id == self.bot.user.id:
            return

        application = Application.objects(confirmation_message=matched_event.tracking_id).first()

        with self._creating_ticket:
            await self._create_application(await self.bot.fetch_user(payload.user_id), application)

            message = await self._verify_channel.fetch_message(matched_event.tracking_id)
            await message.delete()
            matched_event.delete()

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent) -> None:
        """
        Resends the verify message if it was deleted for whatever reason.
        Ensures that no one can just deny an application
        :param payload: The payload for the event
        :type payload: RawMessageDeleteEvent
        """
        matched_event: TrackedEvent = TrackedEvent.objects(tracking_id=payload.message_id,
                                                           event_tag="application").first()
        if not matched_event or self._creating_ticket:
            return

        application = Application.objects(confirmation_message=matched_event.tracking_id).first()
        application_embeds = [Embed.from_dict(d) for d in application.application_embeds]
        confirmation_message = await self._verify_channel.send(embed=application_embeds[0])

        await confirmation_message.add_reaction(CONFIRM_YES)
        matched_event.update(tracking_id=confirmation_message.id)
        application.update(confirmation_message=confirmation_message.id)

    async def _process_application(self, questions: Tuple[str], answers: Tuple[str]) -> None:
        """
        Processes an application. Takes the questions, and answers, and sends the verify message.
        :param questions: The questions for application
        :type questions: Tuple[str]
        :param answers: The applicant's answer to the questions
        :type answers: Tuple[str]
        """
        full_application = dict(zip(questions, answers))
        application = {k: v for k, v in full_application.items() if v}

        name = application[self._config["discord_name_question"]]
        embed_list = self._generate_embeds(name, application)
        confirm_message = await self._verify_channel.send(embed=embed_list[0])

        await confirm_message.add_reaction(CONFIRM_YES)

        TrackedEvent(tracking_id=confirm_message.id,
                     event_tag="application", expire_time=datetime.utcnow() + timedelta(**self._expire_time)).save()
        Application(name=name, confirmation_message=confirm_message.id,
                    application_embeds=[embed.to_dict() for embed in embed_list]).save()

        self._current_applications += 1

    def _generate_embeds(self, name: str, application: dict[str, str]) -> List[embeds.InfoEmbed]:
        """
        Generates a list of embeds for the application.
        Creates the amount of embeds necessary in order to ensure that EMBED_FIELD_MAX isn't surpassed
        :param name: The name of the applicant
        :type name: str
        :param application: The application
        :type application: dict[str, str]
        :return: A list of embeds
        :rtype: List[embeds.InfoEmbed]
        """
        embed_list = []
        if len(application) > EMBED_FIELD_MAX:
            original_app = application
            application = {v: application[v] for i, v in enumerate(application) if i <= EMBED_FIELD_MAX}
            embed_list.extend(self._generate_embeds(name,
                                                    {v: original_app[v] for i, v in enumerate(original_app) if
                                                     i > EMBED_FIELD_MAX}))

        embed_list.append(self._generate_embed(name, application))
        return embed_list[::-1]

    def _generate_embed(self, name: str, application: dict[str, str]) -> embeds.InfoEmbed:
        """
        Generates a singular embed, and ensures that FIELD_CHAR_MAX isn't surpassed for any field.
        :param name: The applicant's name
        :type name: str
        :param application: The user's application
        :type application: dict[str, str]
        :return: The generated embed
        :rtype: embeds.InfoEmbed
        """
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

    async def _create_application(self, voucher: User, application: Application) -> None:
        """
        Creates the ticket for an application once it has been approved.
        :param voucher: The user who vouched the application
        :type voucher: User
        :param application: The appplication to create the ticket for
        :type application: Application
        """
        channel: TextChannel = await (await self.bot.guild()) \
            .create_text_channel(name=f"{application.name.split('#')[0]} application",
                                 category=(await self.bot.fetch_channel(self._config["applications_category"])))

        application_embeds = [Embed.from_dict(d) for d in application.application_embeds]
        messages = [await channel.send(embed=embed) for embed in application_embeds]
        await messages[-1].pin()

        application.update(ticket_id=channel.id)

        voting_message = await self._voting_channel.send(embed=embeds.InfoEmbed(f"Vote for {application.name.split('#')[0]}"))

        try:
            await voting_message.add_reaction(YES_EMOJI)
            await voting_message.add_reaction(NO_EMOJI)
        except HTTPException:
            await voting_message.clear_reactions()
            await voting_message.add_reaction(CHECK_EMOJI)
            await voting_message.add_reaction(CROSS_EMOJI)

        try:
            applicant = list(filter(
                lambda m: m.name == application.name.split("#")[0] and m.discriminator == application.name.split("#")[
                    1],
                (await self.bot.guild()).members))[0]
            await channel.set_permissions(applicant, read_messages=True, send_messages=True, attach_files=True)
            await channel.send(
                f"Thank you for applying {applicant.mention}! Your application has been vouched by {voucher.mention}\nWe will be with you shortly")
        except IndexError:
            await channel.send(
                f"Applicant applied with an invalid discord name, or have left the server. Application vouched by {voucher.mention}")
