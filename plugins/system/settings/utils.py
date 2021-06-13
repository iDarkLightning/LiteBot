import asyncio
import json

from litebot.utils.fmt_strings import CODE_BLOCK

class Timer:
    """
    A configurable timer
    """
    def __init__(self, done, timeout=120):
        self._timeout = timeout
        self._done = done
        self._task = None

    async def start(self):
        """
        Start a timer that will call `self._done` when finished
        """
        self._task = asyncio.create_task(self._sleep())
        await self._task

    async def reset(self):
        """
        Reset the timer
        :return:
        :rtype:
        """
        if self._task:
            self._task.cancel()

        self._task = asyncio.create_task(self._sleep())

    async def stop(self):
        """
        Stop the timer and call `self._done`
        """
        self._task.cancel()
        await self._done()

    def __enter__(self):
        self._task.cancel()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._task = asyncio.create_task(self._sleep())

    async def _sleep(self):
        await asyncio.sleep(self._timeout)
        await self._done()

def pretty_json_code(dict_: dict) -> str:
    """
    Convert a dict to readable JSON string inside a code block
    :param dict_: The dict to convert
    :type dict_: dict
    :return: A readable json string
    :rtype: dict
    """

    return CODE_BLOCK.format("json", {json.dumps(dict_, indent=4)})