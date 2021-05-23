import discord
from discord.ext import commands

from litebot.core import Cog
from litebot.litebot import LiteBot
from litebot.utils.checks import role_checks
from litebot.modules.core.converters import get_server
from litebot.core.minecraft import MinecraftServer
from litebot.utils.fmt_strings import CODE_BLOCK, WHITELIST_ADD, WHITELIST_REMOVE
from litebot.utils.misc import check_role


class ServerCommands(Cog):
    def __init__(self, bot: LiteBot):
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
            if args[0] in [server.name for server in self.bot.servers.all]:
                server = get_server(ctx, args[0])
                command = " ".join(args).partition(f"{server.name} ")[2]
            else:
                server = get_server(ctx, "")
                command = " ".join(args)

        await self._handle_server_command(ctx.channel, ctx.author, server, command)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        A listener that treats commands that start with `/` in bridge channels as a command.
        Equivelant to the `run` command
        :param message: The message sent by the user
        :type message: discord.Message
        """
        if not message.content.startswith("/") or not message.channel.id in [s.bridge_channel_id for s in
                                                                             self.bot.servers.all]:
            return

        server = self.bot.servers[message.channel.id]
        command = message.content.split("/")[1]
        await self._handle_server_command(message.channel, message.author, server, command)

    async def _handle_server_command(self, channel: discord.TextChannel, author: discord.Member,
                                     server: MinecraftServer, command: str) -> None:
        if server.operator:
            if check_role(author, self.bot.config["operators_role"]):
                res = server.send_command(command)
                if res:
                    await channel.send(CODE_BLOCK.format("", res))
            else:
                raise commands.CheckFailure
        else:
            res = server.send_command(command)
            if res:
                await channel.send(CODE_BLOCK.format("", res))

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
        for server in self.bot.servers.all:
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
        for server in self.bot.servers.all:
            whitelist_res = server.send_command(f"whitelist remove {player_name}")
            if player_name in whitelist_res:
                whitelists.append(whitelist_res)

            if not server.operator:
                op_res = server.send_command(f"deop {player_name}")
                if "Nothing" not in op_res:
                    ops.append(op_res)

        await ctx.send(WHITELIST_REMOVE.format(player_name, len(whitelists), player_name, len(ops)))