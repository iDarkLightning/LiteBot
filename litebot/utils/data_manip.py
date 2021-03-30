import re
import datetime
from datetime import datetime, timedelta
from typing import Optional, List
import discord
from discord.utils import get

TIME_KEY = {
    "w": "weeks",
    "d": "days",
    "h": "hours",
    "m": "minutes",
    "s": "seconds"
}

def flatten_dict(dict_: dict, parent_key: Optional[str] = "", separator: Optional[str] = ".") -> dict:
    """
    Flattens a dictionary with the given separator. `.` by default.

    Example Input
    --------------
    {
        "name": "Test",
        "root": {
            "sub": {
                "key": "value"
            }
        }
    }

    Example Output
    ---------------
    {
        "name": "Test",
        "root.sub.key": "value"
    }
    :param dict_: The dictionary to flatten
    :type dict_: dict
    :param parent_key: The parent key
    :type parent_key: Optional[str]
    :param separator: The separator for the sub keys
    :type separator: Optional[str]
    :return: The flattened dictionary
    :rtype: dict
    """
    items = []
    for k, v in dict_.items():
        new_key = (parent_key + separator + k) if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, separator=separator).items())
        else:
            items.append((new_key, v))
    return dict(items)

def unflatten_dict(dict_: dict, separator: Optional[str] = ".") -> dict:
    """
    Unflattens a dictionary, reveres `flatten_dict`
    :param dict_: The dict to unflatten
    :type dict_: dict
    :param separator: The sepearator that was used to flatten the dict
    :type separator: str
    :return: The unflattened dictionary
    :rtype: dict
    """
    result_dict = {}
    for key, value in dict_.items():
        parts = key.split(separator)
        d = result_dict
        for part in parts[:-1]:
            if part not in d:
                d[part] = dict()
            d = d[part]
        d[parts[-1]] = value
    return result_dict

def split_string(str_: str, length: int, sep: Optional[str] = "\n") -> List[str]:
    """
    Splits a string by character limit, on the given seperator
    :param str_: The string to split
    :type str_: str
    :param length: The length of each segment
    :type length: int
    :param sep: The separator that each split will end on
    :type sep: Optional[str]
    :return: Each segment after splitting the string
    :rtype: List[str]
    """
    parts = str_.split(sep)
    res = []
    cur = ""

    for i in parts:
        if len(cur) + len(i) <= length:
            cur += (i + sep)
        else:
            res.append(cur)
            cur = ""
            cur += (i + sep)

    res.append(cur)
    return res

def split_nums_chars(str_: str) -> tuple[str, str]:
    """
    Splits the numbers and characters from a string
    :param str_: The string to split
    :type str_: str
    :return: The characters and the nu
    :rtype: tuple[str, str]
    """
    nums = "".join([i for i in str_ if i.isnumeric()])
    chars = "".join([i for i in str_ if i.isalpha()])

    return chars, nums

def datetime_string_parser(str_: str) -> Optional[datetime]:
    """
    Parse a datetime object from a string
    :param str_:
    :type str_:
    :return:
    :rtype:
    """
    time_regex = re.compile(r"\d+[wdhms]")
    matches = time_regex.findall(str_)
    if matches:
        full = [re.sub(m[-1], TIME_KEY[m[-1]], m) for m in matches]
        time_args = {k: int(v) for k, v in [split_nums_chars(s) for s in full]}
        return datetime.utcnow() + timedelta(**time_args)

def parse_reason(executor: discord.Member, args: tuple[str]) -> str:
    """
    Takes the user's action reason and parses it into a reason with their expire time
    as well as the executor's ID plus the original reason.
    :param executor: The user who used the command
    :type executor: discord.Member
    :param args: The args from the command
    :type args: tuple[str]
    :return: The reason string
    :rtype: str
    """
    if len(args) == 0:
        return f"[{executor.id}]"
    elif len(args) == 1:
        return f"[{datetime_string_parser(args[0])}] [{executor.id}]"
    elif len(args) >= 2:
        ban_time = datetime_string_parser(args[-1])
        if ban_time:
            reason = " ".join(args)
            return f"{reason} [{ban_time}] [{executor.id}]"
        else:
            return f"{' '.join(args)} [{executor.id}]"

def reason_datetime_parser(reason: str) -> Optional[datetime]:
    """
    Gets a datetime object from a reason string.
    The datetime object must be in the right format.
    :param reason: The reason string
    :type reason: str
    :return: The datetime object in the reason string if found
    :rtype: Optional[datetime]
    """
    if not reason:
        return

    if reason.count("[") < 2:
        return

    time_reg = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d+")
    time_str, *_ = time_reg.findall(reason)

    try:
        return datetime.fromisoformat(time_str)
    except ValueError:
        return

async def parse_emoji(bot_instance, message: str) -> str:
    """
    Parses an emoji from your message.
    :param bot_instance: The bot instance
    :type bot_instance: LiteBot
    :param message: The message you are parsing the emoji from
    :type message: str
    :return: The parsed message
    :rtype: str
    """
    emoji_reg = re.compile(r":\w{2,}:")

    if not len(emoji_reg.findall(message)):
        return message

    emoji_name, *_ = emoji_reg.findall(message)

    guild: discord.Guild = await bot_instance.guild
    emoji = get(guild.emojis, name=emoji_name)

    if not emoji:
        return message

    return re.sub(emoji_reg, "{}", message).format(emoji)