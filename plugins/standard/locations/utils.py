import math

from litebot.core.minecraft import ServerCommandContext
from litebot.core.minecraft.commands.arguments import StrictSuggester
from plugins.standard.locations.location_model import Location


class LocationSuggester(StrictSuggester):
    async def suggest(self, ctx: ServerCommandContext, arg: str, prior_args: dict) -> list:
        return [l.location_id.replace(f"{ctx.server.name}_", "") for l in Location.objects() if
                ctx.server.name in l.location_id]

def calculate_2d_distance(points1, points2):
    return math.sqrt(pow(points2[0] - points1[0], 2) + pow(points2[1] - points1[2], 2))

def calculate_3d_distance(points1, points2):
    return math.sqrt(pow(points2[0] - points1[0], 2) + pow(points2[1] - points1[1], 2) + pow(points2[2] - points1[2], 2))