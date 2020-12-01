import discord
from discord.ext import commands, tasks
from discord.utils import get
from PIL import Image, ImageDraw, ImageFont
import math
import io
from rcon import MCRcon

def get_server(client, ctx):
    server_name = list(filter(lambda server: ctx.message.channel.id == client.rcons[server]['bridge_channel'], client.rcons))
    if len(server_name) == 0 or server_name is None:
        raise commands.errors.CommandInvokeError('Not a bridge channel/Not using LTA, enter server_name')
    else:
        return server_name[0]

def perms_check(config_role):
    def predicate(ctx, *args, **kwargs):
        client = ctx.bot
        required_roles = [get(ctx.author.guild.roles, id=role) for role in client.config[config_role]]
        if not any(role in required_roles for role in ctx.author.roles):
            raise commands.CheckFailure
        return True
    return commands.check(predicate)


def scoreboard_image(sort_scores, objective_name, scores_value):
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
    font = ImageFont.truetype(font="./utils/minecraft.ttf", size=20)

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