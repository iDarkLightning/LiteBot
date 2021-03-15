from typing import Optional, List


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

