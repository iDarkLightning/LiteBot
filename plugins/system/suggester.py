from litebot.core import Cog
from litebot.core.minecraft import RPCContext
from litebot.core.minecraft.rpc import rpc


class Suggester(Cog):
    @rpc(name="suggester")
    async def _fetch_suggestions(self, ctx: RPCContext):
        command = self._bot.server_commands[ctx.data["args"]["command_name"]]
        cmd_ctx = command.create_context(ctx.server, self._bot, ctx.data)

        suggestor = command.suggestors[ctx.data["args"]["arg_name"]]()
        return await suggestor.suggest(cmd_ctx)