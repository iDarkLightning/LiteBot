import asyncio
import os
import platform
import shutil
import zipfile
from datetime import datetime, timedelta
from typing import Optional
import jwt
from discord.ext import commands, tasks
from sanic import Sanic
from litebot.core.converters import get_server
from litebot.minecraft import server_commands
from litebot.minecraft.server import MinecraftServer
from litebot.minecraft.server_commands.server_context import ServerContext
from litebot.utils import embeds
from litebot.utils.enums import BackupTypes
from litebot.utils.fmt_strings import BACKUP_INFO, CODE_BLOCK

TIME_FORMAT = '%m-%d-%y %H:%M:%S'
SANIC_APP_NAME = "LiteBot-API"

def creation_time(path):
    if platform.system() == "Windows":
        return os.path.getctime(path)
    else:
        stat = os.stat(path)
        try:
            return stat.st_birthtime
        except AttributeError:
            return stat.st_mtime


class BackupsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self._routine_backups.start()

    @commands.group(name="backup")
    async def _backup(self, ctx: commands.Context) -> None:
        if not ctx.invoked_subcommand:
            await ctx.send_help("backup")

    @_backup.command(name="create")
    async def _backup_create(self, ctx: commands.Context, server_name: Optional[str] = None) -> None:
        server = get_server(ctx, server_name)

        info = BACKUP_INFO.format(server.name, datetime.utcnow(), BackupTypes.MANUAL.value, author=ctx.author)
        if not server.world_dir:
            await ctx.send(embed=embeds.ErrorEmbed("Cannot locate the world directory for this server!"))
            return

        await ctx.send(embed=embeds.InfoEmbed("Creating a backup..."))
        backup_name = await asyncio.to_thread(lambda: self._create_backup(server, BackupTypes.MANUAL, info))
        await ctx.send(embed=embeds.SuccessEmbed(f"Backup {backup_name} Created!"))

    @_backup.command(name="view", aliases=["list"])
    async def _backup_view(self, ctx: commands.Context, server_name: Optional[str] = None) -> None:
        server = get_server(ctx, server_name)

        if not server.backup_dir:
            await ctx.send(embed=embeds.ErrorEmbed("Cannot locate the backup directory for this server!"))
            return

        paths = []
        for root, dirs, files in os.walk(server.backup_dir):
            for file in files:
                paths.append(os.path.join(root, file))

        times = [datetime.fromtimestamp(creation_time(path)).strftime(TIME_FORMAT) for path in paths]
        file_info = dict(zip(paths, times))
        res_str = "\n".join([f"{os.path.basename(path)}: {time}" for path,time in file_info.items()])
        await ctx.send(CODE_BLOCK.format("", res_str))


    @_backup.command(name="load")
    async def _backup_oad(self, ctx: commands.Context, backup_name: str, server_name: Optional[str] = None):
        server = get_server(ctx, server_name)
        backup_path = None

        for root, dirs, files in os.walk(server.backup_dir):
            for file in files:
                if file == backup_name:
                    backup_path = os.path.join(root, file)

        await server.stop()
        if not backup_path:
            await ctx.send(embed=embeds.ErrorEmbed(f"There is no backup for the server {server.name} matching: {backup_name}"))
            return

        await ctx.send(embed=embeds.InfoEmbed(f"Restoring Backup..."))
        await asyncio.to_thread(lambda: self._restore_backup(server, backup_path))
        await ctx.send(embed=embeds.SuccessEmbed(f"Restored Backup {backup_name}. "))

    @_backup.command(name="download")
    async def _backup_download(self, ctx: commands.Context, backup_name: str, server_name: Optional[str] = None) -> None:
        server = get_server(ctx, server_name)
        backup_path = None

        for root, dirs, files in os.walk(server.backup_dir):
            for file in files:
                if file == backup_name:
                    backup_path = os.path.join(root, file)

        if not backup_path:
            await ctx.send(
                embed=embeds.ErrorEmbed(f"There is no backup for the server {server.name} matching: {backup_name}"))
            return

        token = jwt.encode({"server_name": server.name, "exp": datetime.utcnow() + timedelta(minutes=5)},
                           self.bot.config["api_secret"])

        sanic_app = Sanic.get_app(SANIC_APP_NAME)
        url = self.bot.config["api_server_addr"] + \
              sanic_app.url_for("backups.download_backup", backup_name=backup_name, token=token).replace(" ", "%20")

        await ctx.author.send(embed=embeds.InfoEmbed(f"{backup_name}: Download",
                                                     description=url,
                                                     timestamp=datetime.utcnow())
                              .set_footer(text="This link will be valid for the next 5 minutes")
                              .set_thumbnail(url=ctx.author.avatar_url))

    @tasks.loop(hours=24.0)
    async def _routine_backups(self):
        self.bot.logger.info("Starting Routine Backups...")
        current_daily_backups = []
        for server in MinecraftServer.get_all_instances():
            backup_type = BackupTypes.WEEKLY if datetime.today().weekday() == 6 else BackupTypes.DAILY
            info = BACKUP_INFO.format(server.name, datetime.utcnow(), backup_type.value, author=self.bot.user)

            backup_name = await asyncio.to_thread(lambda: self._create_backup(server, backup_type, info))

            if backup_type == BackupTypes.DAILY:
                current_daily_backups.append(f"{backup_name}.zip")
                for file in os.listdir(server.backup_dir):
                    if os.path.isfile(os.path.join(server.backup_dir, file)) and file not in current_daily_backups:
                        os.remove(os.path.join(server.backup_dir, file))

        self.bot.logger.info("Finished Routine Backups!")

    @_routine_backups.before_loop
    async def _before_routine(self):
        await self.bot.wait_until_ready()

    @server_commands.server_command(name="backup")
    async def _server_backup(self, ctx: ServerContext):
        info = BACKUP_INFO.format(ctx.server.name, datetime.utcnow(), BackupTypes.MANUAL.value, author=self.bot.user)

        if not ctx.server.world_dir:
            await ctx.send("Cannot locate the world directory for this server!", 16711680)
            return

        await ctx.send("Creating a backup...", 9869050)
        backup_name = await asyncio.to_thread(lambda: self._create_backup(ctx.server, BackupTypes.MANUAL, info))
        await ctx.send(f"Backup {backup_name} Created!", 3329330)

    def _create_backup(self, server, backup_type, info):
        backup_name = f"[{server.name.upper()} {datetime.utcnow().strftime(TIME_FORMAT)}]"

        if backup_type != BackupTypes.DAILY:
            backup_dir = os.path.join(server.backup_dir, backup_type.value)
        else:
            backup_dir = server.backup_dir

        with zipfile.ZipFile(f"{os.path.join(backup_dir, backup_name)}.zip", "w", compression=zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files, in os.walk(server.world_dir):
                for file in files:
                    path = os.path.join(root, file)
                    z.write(path, os.path.join("backup", os.path.relpath(path, start=server.world_dir)))
            z.writestr("info.txt", info)

        return backup_name

    def _restore_backup(self, server, backup_path):
        with zipfile.ZipFile(backup_path) as zf:
            zf.extractall(server.server_dir)

        os.rename(server.world_dir, os.path.join(server.server_dir, "world-BAK"))
        os.rename(os.path.join(server.server_dir, "backup"), server.world_dir)
        shutil.rmtree(os.path.join(server.server_dir, "world-BAK"))