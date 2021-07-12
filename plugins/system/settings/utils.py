import json

from litebot.utils.fmt_strings import CODE_BLOCK


def pretty_json_code(dict_: dict) -> str:
    """
    Convert a dict to readable JSON string inside a code block
    :param dict_: The dict to convert
    :type dict_: dict
    :return: A readable json string
    :rtype: dict
    """

    return CODE_BLOCK.format("json", json.dumps(dict_, indent=4))