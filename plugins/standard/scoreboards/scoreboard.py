import difflib
import json
from typing import Optional

from discord.ext import commands, tasks
from litebot.core import Cog, Context
from litebot.errors import ServerConnectionFailed
from litebot.utils.markdown import CODE_BLOCK
from litebot.utils.requests import fetch
from plugins.standard.scoreboards.utils import ScoreboardFlag, ScoreboardFlags, scoreboard_image


class Scoreboard(Cog):
    ALL_CMD = "script run scores = {0}; " + \
        "for(scoreboard('{1}'), put(scores, '\"' + _ + '\"', scoreboard('{1}', _))); print(scores)"
    WHITELIST_ONLY_CMD = "script run scores = {0}; " + \
        "for(system_info('server_whitelist'), put(scores, '\"' + _ + '\"', scoreboard('{1}', _))); print(scores)"
    GET_SCOREBOARDS = "script run scoreboard()"
    EVERY_SCOREBOARD_MAPPINGS = "https://raw.githubusercontent.com/samipourquoi/endbot/master/packages/endbot/assets/scoreboards.json"
    MISSING_COMMAND = "Unknown or incomplete command"

    def __init__(self, bot):
        self._server = next(iter(bot.servers.all))
        self._objectives = []
        self._every_board_mappings = {}
        self._refresh_objectives.start()

    @Cog.setting(name="Scoreboard Command", description="View the scores for an in game objective from discord")
    @commands.command(name="scoreboard", aliases=["sb"])
    async def _scoreboard(self, ctx: Context, objective_name: str, flag: Optional[ScoreboardFlag]):
        """
        Generate a scoreboard image for the given objective
        By default, this only includes whitelisted players.

        **Args**:
            `objective_name`: The name of the objective to generate the scoreboard for
        **Flags**:
            `--board | -b`: Show only the players that appear on the ingame sidebar
            `--all | -a`: Show all scoreboard entities instead of just whitelisted players

        """
        cmd = Scoreboard.ALL_CMD if flag else Scoreboard.WHITELIST_ONLY_CMD

        try:
            objective_name = self._every_board_mappings[objective_name]
        except KeyError:
            pass

        res = await self._server.send_command(cmd.format("{}", objective_name))
        scores = sorted({k: int(v) for k, v in json.loads(res.split("} ")[0] + "}").items() if v}.items(),
                        key=lambda x: x[1], reverse=True)
        scores = scores[:15] if flag == ScoreboardFlags.BOARD else scores

        if not scores:
            matches = '\n'.join(difflib.get_close_matches(objective_name, self._objectives, n=3))
            return await ctx.send(
                f"There are no scoreboards named `{objective_name}`! Perhaps you meant {CODE_BLOCK.format('', matches)}") if matches else None

        image = scoreboard_image(scores, objective_name)
        await ctx.send(file=image)

    @tasks.loop(hours=72.0)
    async def _refresh_objectives(self):
        try:
            objectives = await self._server.send_command(Scoreboard.GET_SCOREBOARDS)
            self._objectives = objectives.split("] ")[0].removeprefix("[").split(", ")
        except ServerConnectionFailed:
            pass # Ah well, we'll try next time

        req = await fetch(url=Scoreboard.EVERY_SCOREBOARD_MAPPINGS)
        self._every_board_mappings = json.loads(await req.text())

    def cog_requirements(self, bot):
        try:
            res = self._server.send_sync_command("script run l = [];")
            if Scoreboard.MISSING_COMMAND in res:
                bot.logger.warning(f"Requirements not fulfilled for {self.__cog_name__}: Carpet not installed/script command not enabled on {self._server.name}")
                return False
            return True
        except ServerConnectionFailed:
            bot.logger.warning(f"{self.__cog_name__} unable to load due to {self._server.name} being offline! Please refresh the bot after starting the server!")