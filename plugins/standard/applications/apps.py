import json
from datetime import datetime, timedelta

from discord import TextChannel, Embed, RawReactionActionEvent, RawMessageDeleteEvent, NotFound
from discord.ext import tasks
from gspread import service_account
from gspread.exceptions import APIError

from litebot.core import Cog
from litebot.models import TrackedEvent
from litebot.utils import embeds
from litebot.utils.misc import Toggleable
from plugins.standard.applications.application_model import Application

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
