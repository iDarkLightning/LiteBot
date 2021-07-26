import asyncio
from typing import Callable


class Timer:
    """
    A configurable timer
    """
    def __init__(self, done: Callable, timeout: int = 120):
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