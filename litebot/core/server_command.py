from discord.ext import commands
from litebot.checks import role_checks
from litebot.core.converters import get_server
from litebot.minecraft.server import MinecraftServer
from litebot.utils.fmt_strings import CODE_BLOCK, WHITELIST_ADD, WHITELIST_REMOVE
from litebot.utils.utils import check_role


class ServerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="run", aliases=["execute"])
    @role_checks.config_role_check("members_role")
    async def _run(self, ctx: commands.Context, *args) -> None:
        """
        Allows you to execute a command on the server.
        Any minecraft command that you could normally run, will be usable.
        Leave out the `/` from the command. `gamemode creative` as opposed to `/gamemode creative`.
        If you're not in a bridge channel, the first argument must be the server name.
        Everything after the first argument will be considered as part of the command.
        """
        if len(args) == 0:
            raise commands.errors.CommandInvokeError
        elif len(args) == 1:
            server = get_server(ctx, "")
            command = args[0]
        else:
            if args[0] in [server.name for server in MinecraftServer.get_all_instances()]:
                server = get_server(ctx, args[0])
                command = " ".join(args).partition(f"{server.name} ")[2]
            else:
                server = get_server(ctx, "")
                command = " ".join(args)

        if server.operator:
            if check_role(ctx.author, self.bot.config["operators_role"]):
                await ctx.send(CODE_BLOCK.format("", server.send_command(command)))
            else:
                raise commands.CheckFailure
        else:
            await ctx.send(CODE_BLOCK.format("", server.send_command(command)))

    @commands.group(name="whitelist")
    @role_checks.config_role_check("operators_role")
    async def _whitelist(self, ctx: commands.Context) -> None:
        """
        This is the root command for the whitelist group.
        This command serves no function without
        a subcommand, but will send the help message for this group.
        Essentially invokes `help whitelist`
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help("whitelist")

    @_whitelist.command(name="add")
    async def _whitelist_add(self, ctx: commands.Context, player_name: str) -> None:
        """
        This command whitelists a player on all servers, and OPs them on servers with `operator` set as `False`.
        """
        whitelists = []
        ops = []
        for server in MinecraftServer.get_all_instances():
            whitelist_res = server.send_command(f"whitelist add {player_name}")
            if player_name in whitelist_res:
                whitelists.append(whitelist_res)

            if not server.operator:
                op_res = server.send_command(f"op {player_name}")
                if "Nothing" not in op_res:
                    ops.append(op_res)

        await ctx.send(WHITELIST_ADD.format(player_name, len(whitelists), player_name, len(ops)))

    @_whitelist.command(name="remove")
    async def _whitelist_remove(self, ctx: commands.Context, player_name: str) -> None:
        """
        This command unwhitelists a player on all servers, and DEOPs them from servers where they were whitelisted.
        """
        whitelists = []
        ops = []
        for server in MinecraftServer.get_all_instances():
            whitelist_res = server.send_command(f"whitelist remove {player_name}")
            if player_name in whitelist_res:
                whitelists.append(whitelist_res)

            if not server.operator:
                op_res = server.send_command(f"deop {player_name}")
                if "Nothing" not in op_res:
                    ops.append(op_res)

        await ctx.send(WHITELIST_REMOVE.format(player_name, len(whitelists), player_name, len(ops)))

