import io
import os
import re

from discord import File
from PIL import Image, ImageDraw, ImageFont

JAVA_NUMERIC_PATTERN = re.compile(r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+[dDfF])?)")


def clean_values(value):
    """
    Given a java numeric value, converts it to python number
    """
    match = JAVA_NUMERIC_PATTERN.match(value)
    if match:
        return str(float(match.group(1).lower().removesuffix("d").removesuffix("f")))
    if isinstance(value, str):
        return value.lower()
    return value


def get_mc_font() -> ImageFont:
    """
    Returns a font object for minecraft
    """
    font_path = os.path.join(
        os.getcwd(),
        "plugins",
        "standard",
        "scoreboards",
        "assets",
        "minecraft.ttf",
    )
    return ImageFont.truetype(font_path, size=20)


def text_size(ctx, value, font):
    return ctx.textsize(text=value, font=font, spacing=1)


def get_image(modified_rules) -> File:
    """Get an image of the carpet rules."""
    font = get_mc_font()
    draw = ImageDraw.Draw(Image.new("1", (1, 1)))

    headers = {
        "main": "Modified Carpet Rules",
        "name": "Name",
        "value": "Value",
        "default": "Default",
    }

    header_size = {
        "main": text_size(draw, headers["main"], font),
        "name": text_size(draw, headers["name"], font),
        "value": text_size(draw, headers["value"], font),
        "default": text_size(draw, headers["default"], font),
    }

    columns = {
        "name": "\n".join(modified_rules["name"]),
        "value": "\n".join(modified_rules["value"]),
        "default": "\n".join(modified_rules["default"]),
    }

    column_sizes = {
        "name": text_size(draw, columns["name"], font),
        "value": text_size(draw, columns["value"], font),
        "default": text_size(draw, columns["default"], font),
    }

    column_colors = {
        "name": "#BFBFBF",
        "value": "#FF5555",
        "default": "#5555FF",
    }

    padding = 5

    max_widths = {
        "name": max(header_size["name"][0], column_sizes["name"][0]) + padding * 2,
        "value": max(header_size["value"][0], column_sizes["value"][0]) + padding * 2,
        "default": max(header_size["default"][0], column_sizes["default"][0]) + padding * 2,
    }

    total_width = max(sum(max_widths.values()), header_size["main"][0])
    total_height = sum(
        (
            header_size["main"][1],
            header_size["name"][1],
            column_sizes["name"][1],
            padding * (len(modified_rules["name"]) + 1),
        )
    )

    image = Image.new("RGB", (total_width, total_height), color="#2c2f33")
    draw = ImageDraw.Draw(image)

    text_x = (total_width - header_size["main"][0]) / 2
    text_y = padding

    draw.text(
        xy=(text_x, text_y),
        text=headers["main"],
        fill="#ffffff",
        font=font,
        spacing=padding,
    )

    text_x = padding

    for col in columns.keys():
        text_y = header_size["main"][1] + padding
        draw.text(
            xy=(text_x, text_y),
            text=headers[col],
            fill="#ffffff",
            font=font,
            spacing=padding,
        )
        text_y += header_size[col][1] + padding
        draw.text(
            xy=(text_x, text_y),
            text=columns[col],
            fill=column_colors[col],
            font=font,
            spacing=padding,
        )
        text_x += max_widths[col]

    with io.BytesIO() as buffer:
        image.save(buffer, "png")
        buffer.seek(0)
        rules_image = File(fp=buffer, filename="rules.png")

    return rules_image
