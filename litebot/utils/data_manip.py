from typing import Optional, List, Any

TIME_KEY = {
    "w": "weeks",
    "d": "days",
    "h": "hours",
    "m": "minutes",
    "s": "seconds"
}

def flatten_dict(dict_: dict, parent_key: Optional[str] = "", separator: Optional[str] = ".") -> dict:
    """Flattens a dictionary with the given separator. `.` by default.

    Args:
        dict_: The dictionary to flatten
        parent_key: The parent key
        separator: The separator for the sub keys
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
    """Unflattens a dictionary, reveres `flatten_dict`

    Args:
        dict_: The dictionary to unflatten
        separator: The sepearator that was used to flatten the dict

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
    """Splits a string by character limit, on the given seperator

    Args:
        str_: The string to split
        length: The length of each segment
        sep: The separator that each split will end on

    Returns:
        A list of segments from splitting the string
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
    """Splits the numbers and characters from a string

    Args:
        str_: The string to split

    Returns:
        A tuple containing the characters and the numbers
    """
    nums = "".join([i for i in str_ if i.isnumeric()])
    chars = "".join([i for i in str_ if i.isalpha()])

    return chars, nums

def snakify(str_: str) -> str:
    """Convert a string to snake case

    Args:
        str_: The string to convert
    """
    return str_.replace(" ", "_").lower()