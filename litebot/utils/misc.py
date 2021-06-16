import os
import platform
from typing import List, Union
from PIL import ImageDraw, ImageFont, Image
import math
import io
import discord
from discord.utils import get

from litebot.utils import requests


def check_role(member: discord.Member, role_ids: List[int]) -> bool:
    """
    Checks if a member has any of the roles in a given list of roles.
    :param member: The member to check
    :type member: discord.Member
    :param role_ids: The IDs of the roles to check for
    :type role_ids: List[int]
    :return: Whether the member has atleast any of the given roles
    :rtype: bool
    """
    return any(role in [get(member.guild.roles, id=role) for role in role_ids] for role in member.roles)


def creation_time(path: str) -> Union[float, int]:
    """
    Get's the creation time of a file from its path
    :param path: The path to the file
    :type path: str
    :return: The creation time
    :rtype: Union[float, int]
    """
    if platform.system() == "Windows":
        return os.path.getctime(path)
    else:
        stat = os.stat(path)
        try:
            return stat.st_birthtime
        except AttributeError:
            return stat.st_mtime

async def is_image(url: str) -> bool:
    """
    Check's if a url is to an image
    :param url: The url to check
    :type url: str
    :return: Whether or not the URL is an image
    :rtype: bool
    """
    res = await requests.fetch(url)
    return "image" in res.headers.get("Content-Type")

def calculate_2d_distance(points1, points2):
    return math.sqrt(pow(points2[0] - points1[0], 2) + pow(points2[1] - points1[2], 2))

def calculate_3d_distance(points1, points2):
    return math.sqrt(pow(points2[0] - points1[0], 2) + pow(points2[1] - points1[1], 2) + pow(points2[2] - points1[2], 2))

class Toggleable:
    def __init__(self):
        self._val = False

    def __enter__(self):
        self._val = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._val = False

    def __bool__(self):
        return self._val