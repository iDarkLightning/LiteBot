__plugin_meta__ = {
    "name": "Server Utils!",
    "description": "View server status, and run commands to a server from discord!",
    "authors": ["iDarkLightning"]
}

from datetime import datetime

import discord
from discord.ext import commands

from litebot.core import Cog, Context
from litebot.errors import ServerNotRunningCarpet, ServerConnectionFailed
from litebot.core.minecraft import MinecraftServer
from litebot.utils.embeds import SuccessEmbed, ErrorEmbed
from litebot.utils.fmt_strings import CODE_BLOCK
from litebot.utils.misc import check_role


def get_server(ctx: commands.Context, name: str) -> MinecraftServer:
    if name:
        return ctx.bot.servers[name]
    else:
        return ctx.bot.servers[ctx.channel.id]

class WhitelistActions:
    ADD = "```Whitelisted {player} on {} servers. OPed {player} on {} servers.```"
    REMOVE = "```Unwhitelisted {player} on {} servers. DEOPed {player} on {} servers.```"

class ServerUtils(Cog):
    def __init__(self, bot, plugin):
        self._config = plugin.config

    @Cog.setting(name="Status Command", description="View the status of a server!")
    @commands.command(name="status", aliases=["s", "online", "o"])
    async def _status(self, ctx: Context, server: str = None) -> None:
        """
        Allows you to view the status of a server.
        You must include the server name unless the command is run in a bridge channel.
        `server` The server to display the status for
        """
        server = get_server(ctx, server)
        status = server.status()
        embed = SuccessEmbed(f"{server.name.upper()} Status") if \
            status.online else ErrorEmbed(f"{server.name.upper()} Status")

        embed.description = f"The server is currently {'online' if status.online else 'offline'}!"
        embed.timestamp = datetime.utcnow()

        if status.online:
            try:
                tps, mspt = await server.tps()
                embed.add_field(name="TPS", value=str(mspt), inline=True)
                embed.add_field(name="MSPT", value=str(tps), inline=True)
            except ServerNotRunningCarpet:
                pass

            if len(status.players):
                embed.add_field(name=f"Online Players ({status.players.online}/{status.players.max})",
                                value=status.players, inline=False)

        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f"Requested by: {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @Cog.setting(name="Run Command", description="Execute a command on the server via rcon!")
    @commands.command(name="run", aliases=["execute"])
    async def _run(self, ctx: Context, *args) -> None:
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
            if args[0] in [server.name for server in self._bot.servers.all]:
                server = get_server(ctx, args[0])
                command = " ".join(args).partition(f"{server.name} ")[2]
            else:
                server = get_server(ctx, "")
                command = " ".join(args)

        await self._handle_server_command(ctx.channel, ctx.author, server, command)

    @Cog.setting(
        name="Bridge Channel Commands",
        description="Messages starting with a / in bridge channels get executed to the server as a command")
    @Cog.listener(type=Cog.ListenerTypes.DISCORD, name="on_message")
    async def _bridge_command(self, setting, message):
        if not message.content.startswith("/") or not message.channel.id in [s.bridge_channel_id for s in
                                                                             self._bot.servers.all]:
            return

        server = self._bot.servers[message.channel.id]
        command = message.content.split("/")[1]
        await self._handle_server_command(message.channel, message.author, server, command)

    @Cog.setting(
        name="Whitelist Command",
        description="Easily whitelist someone accross all servers! Also OPs them in servers with operator to set to False")
    @commands.group(name="whitelist")
    async def _whitelist(self, ctx: Context) -> None:
        """
        This is the root command for the whitelist group.
        This command serves no function without
        a subcommand, but will send the help message for this group.
        Essentially invokes `help whitelist`
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help("whitelist")

    @_whitelist.command(name="add")
    async def _whitelist_add(self, ctx: Context, player_name: str) -> None:
        """
        Whitelists a player on all servers, and OPs them on servers with `operator` set as `False`.
        """
        await self._handle_whitelist(ctx, WhitelistActions.ADD, player_name)

    @_whitelist.command(name="remove")
    async def _whitelist_remove(self, ctx: Context, player_name: str) -> None:
        """
        Unwhitelists a player on all servers, and DEOPs them from servers where they were whitelisted.
        """
        await self._handle_whitelist(ctx, WhitelistActions.REMOVE, player_name)

    async def _handle_whitelist(self, ctx: Context, action: str, player_name: str):
        cmds = (
            f"whitelist add {player_name}" if action == WhitelistActions.ADD else f"whitelist remove {player_name}",
            f"op {player_name}" if action == WhitelistActions.ADD else f"deop {player_name}"
        )
        whitelists = []
        ops = []

        for server in self._bot.servers.all:
            try:
                res = await server.send_command(cmds[0])
                if player_name in res:
                    whitelists.append(server.name)
            except ServerConnectionFailed:
                continue

            if not server.operator:
                res = await server.send_command(cmds[1])
                if "Nothing" not in res:
                    ops.append(server.name)

        return await ctx.send(action.format(len(whitelists), len(ops), player=player_name,))

    async def _handle_server_command(self, channel: discord.TextChannel, author: discord.Member,
                                     server: MinecraftServer, command: str) -> None:
        if server.operator:
            if check_role(author, self._config["operators_role"]):
                res = await server.send_command(command)
                if res:
                    await channel.send(CODE_BLOCK.format("", res))
            else:
                raise commands.CheckFailure
        else:
            res = await server.send_command(command)
            if res:
                await channel.send(CODE_BLOCK.format("", res))

def setup(bot):
    bot.add_cog(ServerUtils)

def config(bot):
    return {
        "operators_role": []
    }