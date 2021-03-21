from enum import Enum

"""
A bunch of 'enums' for labelling and easy access
"""

class ModeratorActions(Enum):
    KICK = "Kick"
    BAN = "Ban"
    MUTE = "Mute"
    PARDON = "Pardon"