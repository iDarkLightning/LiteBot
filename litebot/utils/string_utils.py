from typing import Optional, List

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