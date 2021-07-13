import discord
from discord.ext.commands import Converter
from PIL import ImageDraw, ImageFont, Image
import io, os, math

class ScoreboardFlags:
    BOARD = ["--board", "-b"]
    ALL = ["--all", "-a"]

class ScoreboardFlag(Converter):
    async def convert(self, ctx, argument):
        if argument in ScoreboardFlags.ALL:
            return ScoreboardFlags.ALL
        if argument in ScoreboardFlags.BOARD:
            return ScoreboardFlags.BOARD

def scoreboard_image(sort_scores: list[str], objective_name: str) -> discord.File:
    """
    Generates a minecraft scoreboard image for a set of scores.
    :param sort_scores: A list of the player's scores
    :type sort_scores: List[str]
    :param objective_name: The name of the objective scoreboard
    :type objective_name: str
    :return: The generated image
    :rtype: discord.File
    """
    players = []
    scores_value = []

    for i in sort_scores:
        players_value = i[0]
        scores_value_1 = i[1]

        players.append(players_value * 1)
        scores_value.append(scores_value_1 * 1)

    players_final = '\n'.join([str(i) for i in players])
    scores_final = '\n'.join([str(i) for i in scores_value])

    title = objective_name
    total = str(sum(scores_value))

    grey = "#BFBFBF"
    red = "#FF5555"
    white = "#FFFFFF"
    spacing = 1
    font = ImageFont.truetype(font=os.path.join(os.getcwd(), "plugins", "standard", "scoreboards", "assets", "minecraft.ttf"), size=20)

    draw = ImageDraw.Draw(Image.new("1", (1, 1)))

    title_size = draw.textsize(text=title, font=font)
    total_size = draw.textsize(text=total, font=font)
    players_size = draw.multiline_textsize(text=players_final, font=font, spacing=spacing)
    scores_size = draw.multiline_textsize(text=scores_final, font=font, spacing=spacing)

    width = players_size[0] + scores_size[0] + 100
    height = int((((len(players)) * 17) + 36))

    image = Image.new("RGB", (width, height), color="#2c2f33")

    draw = ImageDraw.Draw(image)

    title_pos = (math.floor((width - title_size[0]) / 2), -0.5)
    players_pos = (2, 16)
    scores_pos = (width - scores_size[0] - 1, 16)
    total_pos = (2, players_size[1] + 17)
    total_value_pos = (width - total_size[0] - 1, players_size[1] + 17)

    draw.text(title_pos, text=title, font=font, fill=white)
    draw.text(total_pos, text='Total', font=font, fill=white)
    draw.text(total_value_pos, total, font=font, align="right", fill=red, spacing=1)
    draw.multiline_text(players_pos, players_final, font=font, fill=grey, spacing=1)
    draw.multiline_text(scores_pos, scores_final, font=font, align="right", fill=red, spacing=1)

    final_buffer = io.BytesIO()
    final_buffer.seek(0)

    final_buffer = io.BytesIO()
    image.save(final_buffer, "png")
    final_buffer.seek(0)

    image = discord.File(filename="scoreboard.png", fp=final_buffer)
    return image