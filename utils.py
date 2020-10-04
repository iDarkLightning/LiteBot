from PIL import Image, ImageDraw, ImageFont
import math
import io
import discord
import json
from discord.ext import commands, flags
from discord.utils import get

with open('config.json') as json_file:
    config = json.load(json_file)

def scoreboard_image(sort_scores, objective_name):
    players = []
    scores_value = []

    for i in sort_scores:
        players_value = i[0]
        scores_value_1 = i[1]

        players.append(players_value*1)
        scores_value.append(scores_value_1*1)
        
    players_final = '\n'.join([str(i) for i in players])
    scores_final = '\n'.join([str(i) for i in scores_value])

    title = objective_name
    total = str(sum(scores_value))

    grey = "#BFBFBF"
    red = "#FF5555"
    white = "#FFFFFF"
    spacing = 1
    font = ImageFont.truetype(font="minecraft.ttf", size = 20)

    draw = ImageDraw.Draw(Image.new("1", (1,1)))

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
    draw.multiline_text((players_pos), players_final, font=font, fill=grey, spacing=1)
    draw.multiline_text((scores_pos), scores_final, font=font, align="right", fill=red, spacing=1)

    final_buffer = io.BytesIO()
    final_buffer.seek(0)

    final_buffer = io.BytesIO()
    image.save(final_buffer, "png")
    final_buffer.seek(0)

    image =  discord.File(filename="scoreboard.png", fp=final_buffer)
    return image

def help_embed(embed, command, ctx):
    role = discord.utils.get(ctx.message.author.guild.roles, id=(int(config["members_role"])))
    operator_role = discord.utils.get(ctx.message.author.guild.roles, id=(int(config["operator_role"])))
    if role not in ctx.message.author.roles:
        if str(command) not in ['run', 'tps', 'status', 'scoreboard', 'backup']:
                embed.add_field(name=f'{str(command).capitalize()} Command', value=f'{command.brief}', inline=False)
        if operator_role in ctx.message.author.roles:
            if str(command) == 'backup':
                embed.add_field(name=f'{str(command).capitalize()} Command', value=f'{command.brief}', inline=False)
    else:
        if operator_role not in ctx.message.author.roles:
            if str(command) != 'backup':
                embed.add_field(name=f'{str(command).capitalize()} Command', value=f'{command.brief}', inline=False)  
        else:
            embed.add_field(name=f'{str(command).capitalize()} Command', value=f'{command.brief}', inline=False)
    return embed
    