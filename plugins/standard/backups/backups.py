import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from discord import Message
from discord.ext import commands, tasks

from litebot.core import Cog, Context
from litebot.core.minecraft import ServerCommandContext, Text, Colors, commands as mc_commands
from litebot.server import SERVER_DOMAIN
from litebot.utils import embeds
from litebot.utils.fmt_strings import CODE_BLOCK
from litebot.utils.menus import ConfirmMenu
from plugins.standard.backups.embeds import BackupCreatedEmbed, BackupRestoredEmbed, BackupDownloadEmbed
from plugins.standard.backups.utils import BACKUP_INFO, BackupTypes, create_backup, creation_time, TIME_FORMAT, \
    convert_backup_path, restore_backup


class BackupsCommand(Cog):
    def __init__(self):
        self._routine_backups.start()

    @Cog.setting(
        name="Backup",
        description="Enables you to easily create and restore backups for your servers, directly from discord!")
    @commands.group(name="backup")
    async def _backup(self, ctx: Context) -> None:
        """
        Root command for the backup group.
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help("backup")

    @_backup.command(name="create")
    async def _backup_create(self, ctx: Context, server_name: Optional[str]) -> Message:
        """
        Create a backup for a server.
        **Args**:
            `server_name` The name of the server that you are creating a backup for
        """
        server = self._bot.servers.get_server(ctx, server_name)

        if not server.world_dir:
            return await ctx.send(embed=embeds.ErrorEmbed("Cannot locate the world directory for this server!"))

        info = BACKUP_INFO.format(server.name, datetime.utcnow(), BackupTypes.MANUAL.value, author=ctx.author)
        async with ctx.typing():
            msg = await ctx.send(embed=embeds.InfoEmbed("Creating a backup..."))
            backup_name, backup_path = await asyncio.to_thread(create_backup, server, BackupTypes.MANUAL, info)
            await msg.delete()
            await ctx.send(embed=BackupCreatedEmbed(server, backup_name, backup_path, ctx.author))

    @_backup.command(name="view", aliases=["list"])
    async def _backup_view(self, ctx: Context, server_name: Optional[str]) -> Message:
        """
        View all the backups for a server
        **Args**:
            `server_name` The name of the server that you are creating a backup for
        """
        server = self._bot.servers.get_server(ctx, server_name)

        if not server.backup_dir:
            return await ctx.send(embed=embeds.ErrorEmbed("Cannot locate the backup directory for this server!"))

        paths = []
        for root, dirs, files in os.walk(server.backup_dir):
            for file in files:
                paths.append(os.path.join(root, file))

        times = [datetime.fromtimestamp(creation_time(path)).strftime(TIME_FORMAT) for path in paths]
        file_info = dict(zip(paths, times))
        res_str = "\n".join([f"{os.path.basename(path)}: {time}" for path, time in file_info.items()])
        await ctx.send(CODE_BLOCK.format("", res_str))

    @_backup.command(name="load", aliases=["restore"])
    async def _backup_load(self, ctx: Context, backup_name: str, server_name: Optional[str]) -> Message:
        """
        Restore a backup for a server.
        If you are not running LiteHost, you will have to manually start the server after the backup has been restored.

        **Args**:
            `server_name` The name of the server that you are creating a backup for
            `backup_name` The name of the backup you are restoring
        """
        server = self._bot.servers.get_server(ctx, server_name)
        backup_path = convert_backup_path(backup_name, server)

        if not backup_path:
            return await ctx.send(embed=embeds.ErrorEmbed(
                f"There is no backup for the server {server.name} matching: {backup_name}"))

        confirm = await ConfirmMenu(
            f"Are you sure you would like to restore the backup: {backup_name} for {server_name}?").prompt(ctx)
        if not confirm:
            return await ctx.send(embed=embeds.ErrorEmbed("Aborted!"))

        async with ctx.typing():
            msg = await ctx.send(embed=embeds.InfoEmbed(f"Restoring Backup..."))
            await server.stop()

            try:
                await asyncio.to_thread(restore_backup, server, backup_path)
                await server.start()
            except Exception as e:
                return await ctx.send(embed=embeds.ErrorEmbed(f"Failed to restore backup! {e}"))

            await msg.delete()
            await ctx.send(embed=BackupRestoredEmbed(server, ctx.author))

    @_backup.command(name="download")
    async def _backup_download(self, ctx: Context, backup_name: str, server_name: Optional[str]) -> Message:
        """
        Download a backup for a server.
        **Args**:
            `server_name` The name of the server that you are creating a backup for
            `backup_name` The name of the backup you are restoring
        """
        server = self._bot.servers.get_server(ctx, server_name)
        backup_path = convert_backup_path(backup_name, server)

        if not backup_path:
            return await ctx.send(embed=embeds.ErrorEmbed(
                f"There is no backup for the server {server.name} matching: {backup_name}"))

        token = jwt.encode({"server_name": server.name, "exp": datetime.utcnow() + timedelta(minutes=5)},
                           self._bot.config["api_secret"])

        url = SERVER_DOMAIN + self._bot.server.url_for("backups.download_backup", backup_name=backup_name, token=token)\
                                .replace(" ", "%20")

        await ctx.author.send(embed=BackupDownloadEmbed(server, backup_name, url))

    @Cog.setting(name="Server Backups",
                 description="Enables you to easily create backups directly from the server!")
    @mc_commands.command(name="backup")
    async def _server_backup(self, ctx: ServerCommandContext):
        """
        Create a backup of the server world
        """
        info = BACKUP_INFO.format(ctx.server.name, datetime.utcnow(), BackupTypes.MANUAL.value, author=ctx.player)
        if not ctx.server.world_dir:
            return await ctx.send(text=Text().add_component(
                text="Could not find the backup directory for this server", color=Colors.DARK_RED))

        await ctx.send(text=Text().add_component(text="Creating a backup...", color="#9696FA"))
        backup_name, _ = await asyncio.to_thread(create_backup, ctx.server, BackupTypes.MANUAL, info)
        await ctx.send(
            text=Text().add_component(text=f"Backup {backup_name} created successfully", color="#32CD32"))

    @Cog.setting(name="Routine Backups",
                 description="Automatically takes backups every 24 hours. These backups are considered daily backups, and are replaced by the next days backups. However, backups taken on a sunday are considered to be a weekly backup, and will never be deleted.")
    @tasks.loop(hours=24.0)
    async def _routine_backups(self):
        self._bot.logger.info("Starting Routine Backups...")
        current_daily_backups = []

        for server in [s for s in self._bot.servers.all if s.backup_dir]:
            backup_type = BackupTypes.WEEKLY if datetime.today().weekday() == 6 else BackupTypes.DAILY
            info = BACKUP_INFO.format(server.name, datetime.utcnow(), backup_type.value, author=self._bot.user)

            backup_name, _ = await asyncio.to_thread(create_backup, server, backup_type, info)

            if backup_type == BackupTypes.DAILY:
                current_daily_backups.append(f"{backup_name}.zip")
                for file in os.listdir(server.backup_dir):
                    if os.path.isfile(os.path.join(server.backup_dir, file)) and file not in current_daily_backups:
                        os.remove(os.path.join(server.backup_dir, file))

            self._bot.logger.info(f"Finished Routine Backups For {server.name.upper()}")

        self._bot.logger.info("Finished Routine Backups!")

    @_routine_backups.before_loop
    async def _before_routine_backups(self):
        await self._bot.wait_until_ready()

    def cog_requirements(self, bot):
        for server in bot.servers.all:
            if server.world_dir:
                return True

        return bot.logger.warning("In order to use Backups, you must mount at least one of your server directories!")
