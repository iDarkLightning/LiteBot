from typing import Optional

from datetime import datetime

from discord import Message
from discord.ext import commands as dc_commands
from mongoengine import NotUniqueError

from litebot.core import Cog
from litebot.minecraft import commands
from litebot.minecraft.commands.arguments import BlockPosArgumentType, IntegerArgumentType, DimensionArgumentType, \
    StringArgumentType, StrictSuggester, PlayerArgumentType
from litebot.minecraft.commands.context import ServerCommandContext
from litebot.minecraft.text import Text, Colors
from litebot.models.location_model import Location
from litebot.utils import embeds
from litebot.utils.data_manip import snakify


class LocationSuggester(StrictSuggester):
    async def suggest(self, ctx: ServerCommandContext, arg: str, prior_args: dict) -> list:
        return [l.location_id for l in Location.objects()]

class LocationCommand(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="location")
    async def _location(self, ctx: ServerCommandContext):
        """
        A namespace for declaring /location commands
        """
        pass

    @_location.sub(name="add")
    async def _location_add(self,
                            ctx: ServerCommandContext,
                            name: StringArgumentType,
                            vec3: Optional[BlockPosArgumentType]=None,
                            dimension: Optional[DimensionArgumentType]=None,
                            tolerance: Optional[IntegerArgumentType]=None) -> None:
        try:
            pos_x = vec3[0]
            pos_y = vec3[1]
            pos_z = vec3[2]
        except TypeError:
            pos_x = ctx.player.pos_x
            pos_y = ctx.player.pos_y
            pos_z = ctx.player.pos_z

        dimension = dimension or ctx.player.dimension

        try:
            Location(location_id=snakify(name), name=name, dimension=dimension, coordinates=[pos_x, pos_y, pos_z], tolerance=tolerance).save()
            await ctx.send(text=Text().add_component(text=f"New location: {name} has been added at {pos_x}, {pos_y}, {pos_z}", color=Colors.GREEN))
        except NotUniqueError:
            await ctx.send(text=Text().add_component(text=f"There is already a location with the name {name}", color=Colors.RED))

    @_location.sub(name="get")
    async def _location_get(self, ctx: ServerCommandContext, name: LocationSuggester) -> None:
        location = Location.objects(location_id=name).first()
        t = Text()
        t.add_component(text=location.name, color=Colors.DARK_PURPLE)
        t.add_component(text=" is at ", color=Colors.WHITE)


        t.add_component(text=f"X:{location.coordinates[0]}, Y:{location.coordinates[1]}, Z: {location.coordinates[2]}",
                        color=Colors.AQUA)


        t.add_component(text=" in ", color=Colors.WHITE)
        t.add_component(text=location.dimension, color=Colors.AQUA)
        await ctx.send(text=t)

    @_location.sub(name="remove", op_level=1)
    async def _location_remove(self, ctx: ServerCommandContext, name: LocationSuggester) -> None:
        location = Location.objects(location_id=name).first()
        location.delete()

        await ctx.send(text=Text().add_component(text=f"Removed the location {location.name}!", color=Colors.GREEN))

    @dc_commands.command(name="locate")
    async def _discord_location_get(self, ctx: dc_commands.Context, *, name: str) -> Optional[Message]:
        location = Location.objects(name=name).first()

        if not location:
            return await ctx.send(embed=embeds.ErrorEmbed(
                f"There is no available location with the name {name}!\n The available locations are: ",
                description="\n".join([l.name for l in Location.objects()])))

        e = embeds.InfoEmbed(location.name, timestamp=datetime.utcnow())
        e.add_field(name="Location: ", value=f"X:{location.coordinates[0]}, Y:{location.coordinates[1]}, Z: {location.coordinates[2]}")
        e.add_field(name="Dimension: ", value=location.dimension)
        e.set_footer(text=f"Requested By: {ctx.author.name}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=e)

    @commands.command(name="pos")
    async def _pos(self, ctx: ServerCommandContext, player: Optional[PlayerArgumentType]):
        pass


