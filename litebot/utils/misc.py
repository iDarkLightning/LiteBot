from typing import List
import discord
from discord.utils import get


def check_role(member: discord.Member, role_ids: List[int]) -> bool:
    """Checks if a member has any of the roles in a given list of roles.

    Args:
        member: The member to check
        role_ids: The IDs of the roles to check the member for
    """
    return any(role in [get(member.guild.roles, id=role) for role in role_ids] for role in member.roles)

class Toggleable:
    """
    A class letting you toggle true or false using a context manager
    """
    def __init__(self):
        self._val = False

    def __enter__(self):
        self._val = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._val = False

    def __bool__(self):
        return self._val