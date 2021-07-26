from typing import Union

from discord import Embed, AllowedMentions, InvalidArgument
from discord.http import Route
from discord_components import Interaction as DCInteraction, Component, FlagsType, \
    DiscordComponents as DCDiscordComponents, Select


class Interaction(DCInteraction):
    @property
    def id(self):
        return int(self.raw_data["d"]["message"]["id"])

    async def edit(self, *, content: str = None, embed: Embed = None, embeds: list[Embed] = None,
                   allowed_mentions: AllowedMentions = None, tts: bool = False, ephemeral: bool = True,
                   components: list[Union[Component, list[Component]]] = None, **options) -> None:
        """Edit a server interaction object

        Args:
            content: The content of the edited message
            embed: The embed of the edited message
            embeds: A list of embeds for the edited message
            allowed_mentions: The people the message is allowed to ping
            tts: Whether or not the message is TTS
            ephemeral: Whether or not the message is ephemeral
            components: The components attached to the edited message
            **options: Any extra options
        """


        state = self.bot._get_state()
        data = {
            **self.client._get_components_json(components),
            **options,
            "flags": FlagsType.Ephemeral if ephemeral else 0
        }

        if content is not None:
            data["content"] = content

        if embed and embeds:
            embeds.append(embed)
        elif embed:
            embeds = [embed]

        if embeds:
            embeds = list(map(lambda x: x.to_dict(), embeds))
            if len(embeds) > 10:
                raise InvalidArgument("Embed limit exceeded. (Max: 10)")
            data["embeds"] = embeds

        if allowed_mentions:
            if state.allowed_mentions:
                allowed_mentions = state.allowed_mentions.merge(allowed_mentions).to_dict()
            else:
                allowed_mentions = allowed_mentions.to_dict()

            data["allowed_mentions"] = allowed_mentions

        if tts is not None:
            data["tts"] = tts

        await self.bot.http.request(
            Route("PATCH",
                  f"/webhooks/{self.bot.user.id}/{self.interaction_token}/messages/@original"),
            json=data
        )

class DiscordComponents(DCDiscordComponents):
    def _get_interaction(self, json: dict):
        data = self._structured_raw_data(json)
        rescomponent = []

        if data["message"]:
            for component in data["message"].components:
                if isinstance(component, Select):
                    for option in component.options:
                        if option.value in data["values"]:
                            if len(data["values"]) > 1:
                                rescomponent.append(option)
                            else:
                                rescomponent = [option]
                                break
                else:
                    if component.id == data["component"]["custom_id"]:
                        rescomponent = component
        else:
            rescomponent = data["component"]

        ctx = Interaction(
            bot=self.bot,
            client=self,
            user=data["user"],
            component=rescomponent,
            raw_data=data["raw"],
            message=data["message"],
            is_ephemeral=not bool(data["message"]),
        )
        return ctx