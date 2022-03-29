import json
import re

from discord.ext import commands, tasks
from litebot.core import Cog, Context
from litebot.core.minecraft import MinecraftServer
from litebot.errors import ServerConnectionFailed
from litebot.utils.requests import fetch
from plugins.standard.carpet_rules import utils
from plugins.standard.carpet_rules.utils import clean_values
from plugins.standard.scoreboards import Scoreboard
from plugins.standard.server_utils import get_server


class CarpetRulesCommand(Cog):
    RULES_DATABASE_URL = "https://raw.githubusercontent.com/Crec0/carpet-rules-database/main/data/parsed_data.json"

    def __init__(self, bot):
        self._bot = bot
        self._all_rules = {}
        self.refresh_rules.start()

    @Cog.setting(
        name="Carper Rules",
        desc="Get a list of modified carpet rules from the server.",
    )
    @commands.command(name="cr", aliases=["carpet_rules"])
    async def _cr(self, ctx: Context, server: str = None):
        """Get a list of modified carpet rules from the server."""
        server = get_server(ctx, server)
        if not await self.try_sync_server(server, ctx):
            return
        rules_ret = await server.send_command(
            "script run encode_json(system_info('world_carpet_rules'))"
        )
        rules_ret = re.sub("^[^{]*", "", rules_ret)
        rules_ret = re.sub("[^}]+$", "", rules_ret)
        json_rules = json.loads(rules_ret)

        modified_rules: dict = {
            "name": [],
            "value": [],
            "default": [],
        }

        for name, val in json_rules.items():
            try:
                default = self._all_rules[name]
            except KeyError:
                default = "UNKNOWN"
            str_val = clean_values(val)
            str_default = clean_values(default)
            if str_val != str_default:
                modified_rules["name"].append(name)
                modified_rules["value"].append(str_val)
                modified_rules["default"].append(str_default)

        await ctx.send(file=utils.get_image(modified_rules))

    @tasks.loop(hours=96)
    async def refresh_rules(self):
        req = await fetch(url=CarpetRulesCommand.RULES_DATABASE_URL)
        json_rules = json.loads(await req.text())
        self._all_rules.clear()
        for rule in json_rules:
            self._all_rules[rule["name"]] = rule["value"]

    async def try_sync_server(self, server: MinecraftServer, ctx: Context) -> bool:
        try:
            res = server.send_sync_command("script run l = [];")
            if Scoreboard.MISSING_COMMAND in res:
                rep = f"Requirements not fulfilled for {self.__cog_name__}: " \
                      f"Carpet not installed/script command not enabled on {server.name}"
                self._bot.logger.warning(rep)
                await ctx.send(rep)
                return False
            return True
        except ServerConnectionFailed:
            rep = f"{self.__cog_name__} unable to load due to {server.name} being offline! " \
                  f"Please refresh the bot after starting the server!"
            self._bot.logger.warning(rep)
            await ctx.send(rep)
            return False
