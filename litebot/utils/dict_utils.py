from typing import Optional


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