import json
from typing import Optional

from datetime import datetime

from discord import Message
from discord.ext import commands as dc_commands
from mongoengine import NotUniqueError

from litebot.core import Cog
from litebot.litebot import LiteBot
from litebot.minecraft import commands
from litebot.minecraft.commands.arguments import BlockPosArgumentType, IntegerArgumentType, DimensionArgumentType, \
    StringArgumentType, StrictSuggester, PlayerArgumentType
from litebot.minecraft.commands.context import ServerCommandContext
from litebot.minecraft.player import Player
from litebot.minecraft.text import Text, Colors
from litebot.models.location_model import Location
from litebot.utils import embeds
from litebot.utils.data_manip import snakify
from litebot.utils.misc import calculate_3d_distance, calculate_2d_distance


class LocationSuggester(StrictSuggester):
    async def suggest(self, ctx: ServerCommandContext, arg: str, prior_args: dict) -> list:
        return [l.location_id.replace(f"{ctx.server.name}_", "") for l in Location.objects() if
                ctx.server.name in l.location_id]

class LocationCommand(Cog):
    def __init__(self, bot: LiteBot) -> None:
        self.bot = bot

    @commands.command(name="location")
    async def _location(self, ctx: ServerCommandContext) -> None:
        """
        A namespace for declaring /location commands
        """
        pass

    @_location.sub(name="add")
    async def _location_add(self,
                            ctx: ServerCommandContext,
                            name: StringArgumentType,
                            block_pos: Optional[BlockPosArgumentType] = None,
                            dimension: Optional[DimensionArgumentType] = None,
                            tolerance: Optional[IntegerArgumentType] = None) -> None:
        """
        Add a new location
        `name` The name of the location
        `block_pos` The coordinates of the location
        `dimension` The dimension of the location
        `tolerance` The radius in which a player will be considered to be present at this location
        """
        try:
            pos_x = block_pos[0]
            pos_y = block_pos[1]
            pos_z = block_pos[2]
        except TypeError:
            pos_x = ctx.player.pos_x
            pos_y = ctx.player.pos_y
            pos_z = ctx.player.pos_z

        dimension = dimension or ctx.player.dimension

        try:
            l = Location(location_id=f"{ctx.server.name}_{snakify(name)}", name=name, dimension=dimension,
                     coordinates=[pos_x, pos_y, pos_z], tolerance=tolerance).save()
            await ctx.send(text=Text().add_component(
                text=f"New location: {name} has been added at {pos_x}, {pos_y}, {pos_z}", color=Colors.GREEN))
        except NotUniqueError:
            await ctx.send(text=Text().add_component(text=f"There is already a location with the name {name}",
                                                     color=Colors.RED))

    @_location.sub(name="get")
    async def _location_get(self, ctx: ServerCommandContext, name: LocationSuggester) -> None:
        """
        Get the coordinates of a location
        `name` The name of the location to get coordinates for
        """
        location = Location.objects(location_id=f"{ctx.server.name}_{name}").first()
        ctx["location"] = location.to_json()
        t = Text()
        t.add_component(text=location.name, color=Colors.DARK_PURPLE)
        t.add_component(text=" is at ", color=Colors.WHITE)


        t.add_component(text=f"X:{location.coordinates[0]}, Y:{location.coordinates[1]}, Z: {location.coordinates[2]}",
                        color=Colors.AQUA)

        pos_x, pos_z = None, None
        if location.dimension == "minecraft:overworld":
            pos_x = location.coordinates[0] // 8
            pos_z = location.coordinates[2] // 8
        elif location.dimension == "minecraft:the_nether":
            pos_x = location.coordinates[0] * 8
            pos_z = location.coordinates[2] * 8

        t.add_component(text=" in ", color=Colors.WHITE)
        t.add_component(text=location.dimension, color=Colors.AQUA)

        if pos_x and pos_z:
            conversion_dimension = "minecraft:the_nether" if location.dimension == "minecraft:overworld" else location.dimension
            t.add_component(text="\nThe location in ", color=Colors.WHITE)
            t.add_component(text=conversion_dimension, color=Colors.AQUA)
            t.add_component(text=" is ", color=Colors.WHITE)
            t.add_component(text=f"X:{pos_x}, Z:{pos_z}", color=Colors.AQUA)

        await ctx.send(text=t)

    @_location.sub(name="remove", op_level=1)
    async def _location_remove(self, ctx: ServerCommandContext, name: LocationSuggester) -> None:
        """
        Remove an added location
        `name` The name of the location to remove
        """
        location = Location.objects(location_id=f"{ctx.server.name}_{name}").first()
        location.delete()

        await ctx.send(text=Text().add_component(text=f"Removed the location {location.name}!", color=Colors.GREEN))

    @dc_commands.command(name="locate")
    async def _discord_location_get(self, ctx: dc_commands.Context, *, name: str) -> Optional[Message]:
        """
        Get the coordinates of a location
        `name` The name of the location to get the coordinates for
        """
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
    async def _pos(self, ctx: ServerCommandContext, player: Optional[PlayerArgumentType] = None) -> None:
        """
        Get the position of a player
        `player` The player to get the position of
        """
        player = player or ctx.player

        t = Text()
        t.add_component(text=player.name, color=Colors.DARK_PURPLE)
        t.add_component(text=" is at ", color=Colors.WHITE)
        t.add_component(text=f"X:{player.pos_x}, Y:{player.pos_y}, Z:{player.pos_z}", color=Colors.AQUA)
        t.add_component(text=" in ", color=Colors.WHITE)
        t.add_component(text=player.dimension, color=Colors.AQUA)

        locations = [l for l in Location.objects() if l.tolerance is not None]
        distances = {l.name: calculate_3d_distance(l.coordinates, player.get_block_pos()) for l in locations}

        print(distances)

        t = self._add_distances(distances, t)
        await ctx.send(text=t)

    @_pos.sub(name="convert")
    async def _pos_convert(self, ctx: ServerCommandContext) -> None:
        """
        Convert a player's position to the overworld if they are in the nether and to the nether if they are in the overworld
        """
        player = Player(**json.loads(ctx.full_args.get("player")))

        if player.dimension == "minecraft:overworld":
            pos_x = player.pos_x // 8
            pos_z = player.pos_z // 8
        elif player.dimension == "minecraft:the_nether":
            pos_x = player.pos_x * 8
            pos_z = player.pos_z * 8
        else:
            return await ctx.send(text=Text().add_component(text="Conversion only works between the overworld and the nether!", color=Colors.RED))

        conversion_dimension = "minecraft:the_nether" if player.dimension == "minecraft:overworld" else player.dimension

        t = Text()
        t.add_component(text="The position of ", color=Colors.WHITE)
        t.add_component(text=player.name, color=Colors.DARK_PURPLE)
        t.add_component(text=f" in ", color=Colors.WHITE)
        t.add_component(text=conversion_dimension, color=Colors.AQUA)
        t.add_component(text=f" is ", color=Colors.WHITE)
        t.add_component(text=f"X:{pos_x}, Z:{pos_z}", color=Colors.AQUA)

        locations = [l for l in Location.objects(dimension=conversion_dimension) if l.tolerance is not None]
        distances = {l.name: calculate_2d_distance(l.coordinates, (pos_x, pos_z)) for l in locations}

        t = self._add_distances(distances, t)
        await ctx.send(text=t)

    def _add_distances(self, distances: dict[str, int], text: Text) -> Text:
        for name, distance in distances.items():
            location = Location.objects(name=name).first()

            if distance <= location.tolerance:
                text.add_component(text="\n≈", color=Colors.WHITE)
                text.add_component(text=f"{int(distance)}", color=Colors.AQUA)
                text.add_component(text=" blocks away from ", color=Colors.WHITE)
                text.add_component(text=location.name, color=Colors.DARK_PURPLE)

        return text