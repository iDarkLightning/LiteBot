import asyncio
import os
import shutil
import zipfile
from datetime import datetime, timedelta
from typing import Optional
import jwt
from discord.ext import commands, tasks
from sanic import Sanic

from litebot.core import Cog
from litebot.utils.checks import role_checks
from litebot.modules.core.converters import get_server
from litebot.core.minecraft import commands as mc_commands
from litebot.core.minecraft import MinecraftServer
from litebot.core.minecraft import ServerCommandContext
from litebot.core.minecraft.text import Text, Colors
from litebot.modules.backups.converters import convert_backup_path
from litebot.utils import embeds
from litebot.utils.enums import BackupTypes
from litebot.utils.fmt_strings import BACKUP_INFO, CODE_BLOCK
from litebot.utils.misc import creation_time

TIME_FORMAT = '%m-%d-%y %H-%M-%S'
SANIC_APP_NAME = "LiteBot-API"


def _create_backup(server: MinecraftServer, backup_type: BackupTypes, info: str) -> str:
    """
    Creates a backup for a server.
    :param server: The server that you are creating a backup for.
    :type server: MinecraftServer
    :param backup_type: The type of the backup you are creating
    :type backup_type: BackupTypes
    :param info: The info string for the backup
    :type info: str
    :return: The name of the backup created
    :rtype: str
    """
    backup_name = f"[{server.name.upper()} {datetime.utcnow().strftime(TIME_FORMAT)}]"

    if backup_type != BackupTypes.DAILY:
        backup_dir = os.path.join(server.backup_dir, backup_type.value)
    else:
        backup_dir = server.backup_dir

    with zipfile.ZipFile(f"{os.path.join(backup_dir, backup_name)}.zip", "w", compression=zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files, in os.walk(server.world_dir):
            for file in files:
                if file == "session.lock":
                    continue

                path = os.path.join(root, file)
                z.write(path, os.path.join("backup", os.path.relpath(path, start=server.world_dir)))
        z.writestr("info.txt", info)

    return backup_name

def _restore_backup(server: MinecraftServer, backup_path: str) -> None:
    """
    Restores a backup for a server
    :param server: The server that you are restoring the backup for
    :type server: MinecraftServer
    :param backup_path: The path to the backup being restored
    :type backup_path: str
    """
    with zipfile.ZipFile(backup_path) as zf:
        zf.extractall(server.server_dir)

    try:
        os.rename(server.world_dir, os.path.join(server.server_dir, "world-BAK"))
        os.rename(os.path.join(server.server_dir, "backup"), server.world_dir)
        shutil.rmtree(os.path.join(server.server_dir, "world-BAK"))
    except Exception:
        os.rename(os.path.join(server.server_dir, "world-BAK"), server.world_dir)
        raise Exception


class BackupsCommand(Cog):
    def __init__(self, bot):
        self.bot = bot
        self._routine_backups.start()

    @commands.group(name="backup")
    @role_checks.module_config_role_check("backup_role", module_name="backups")
    async def _backup(self, ctx: commands.Context) -> None:
        """
        This is the root command for the backup group.
        This command serves no function without
        a subcommand, but will send the help message for this group.
        Essentially invokes `help backup`
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help("backup")

    @_backup.command(name="create")
    async def _backup_create(self, ctx: commands.Context, server_name: Optional[str]) -> None:
        """
        This commands lets you create a backup for a server.
        `server_name` The name of the server that you are creating a backup for
        """
        server = get_server(ctx, server_name)

        info = BACKUP_INFO.format(server.name, datetime.utcnow(), BackupTypes.MANUAL.value, author=ctx.author)
        if not server.world_dir:
            await ctx.send(embed=embeds.ErrorEmbed("Cannot locate the world directory for this server!"))
            return

        await ctx.send(embed=embeds.InfoEmbed("Creating a backup..."))
        backup_name = await asyncio.to_thread(lambda: _create_backup(server, BackupTypes.MANUAL, info))
        await ctx.send(embed=embeds.SuccessEmbed(f"Backup {backup_name} Created!"))

    @_backup.command(name="view", aliases=["list"])
    async def _backup_view(self, ctx: commands.Context, server_name: Optional[str]) -> None:
        """
        This command lets you view all the backups for a server
        `server_name` The name of the server that you are creating a backup for
        """
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

    @_backup.command(name="load", aliases=["restore"])
    async def _backup_load(self, ctx: commands.Context, backup_name: str, server_name: Optional[str]):
        """
        This command lets you load a backup for a server.
        The server will be stopped automatically, but you will have to start it after.
        `backup_name` The name of the backup you are restoring
        `server_name` The name of the server that you are creating a backup for
        """
        server = get_server(ctx, server_name)
        backup_path = convert_backup_path(backup_name, server)

        if not backup_path:
            await ctx.send(embed=embeds.ErrorEmbed(f"There is no backup for the server {server.name} matching: {backup_name}"))
            return

        await ctx.send(embed=embeds.InfoEmbed(f"Restoring Backup..."))
        await server.stop()

        try:
            await asyncio.to_thread(lambda: _restore_backup(server, backup_path))
        except Exception as e:
            await ctx.send(embed=embeds.ErrorEmbed(f"Failed to restore backup! {e}"))
            return
        await ctx.send(embed=embeds.SuccessEmbed(f"Restored Backup {backup_name}. "))

    @_backup.command(name="download")
    async def _backup_download(self, ctx: commands.Context, backup_name: str, server_name: Optional[str]) -> None:
        """
        This command lets you download a backup for a server.
        `backup_name` The name of the backup you are restoring
        `server_name` The name of the server that you are creating a backup for
        """
        server = get_server(ctx, server_name)
        backup_path = convert_backup_path(backup_name, server)

        if not backup_path:
            await ctx.send(embed=embeds.ErrorEmbed(
                f"There is no backup for the server {server.name} matching: {backup_name}"))
            return

        token = jwt.encode({"server_name": server.name, "exp": datetime.utcnow() + timedelta(minutes=5)},
                           self.bot.config["api_secret"])

        sanic_app = Sanic.get_app(SANIC_APP_NAME)
        url = sanic_app.url_for("backups.download_backup", backup_name=backup_name, token=token,
                                _external=True, _scheme="http").replace(" ", "%20")

        await ctx.author.send(embed=embeds.InfoEmbed(f"{backup_name}: Download",
                                                     description=f"[Click to download]({url})",
                                                     timestamp=datetime.utcnow())
                              .set_footer(text="This link will be valid for the next 5 minutes"))

    @tasks.loop(hours=24.0)
    async def _routine_backups(self):
        """
        This is a routine task that handles daily backups.
        Backups will be made in 24 hour intervals that will replace the previous days backup.
        If the current day is a sunday, then a weekly backup will be made instead.
        Weekly backups are stored forever, or until you manually delete them.
        """
        self.bot.logger.info("Starting Routine Backups...")
        current_daily_backups = []
        for server in [s for s in self.bot.servers.all if s.backup_dir]:
            backup_type = BackupTypes.WEEKLY if datetime.today().weekday() == 6 else BackupTypes.DAILY
            info = BACKUP_INFO.format(server.name, datetime.utcnow(), backup_type.value, author=self.bot.user)

            backup_name = await asyncio.to_thread(lambda: _create_backup(server, backup_type, info))

            if backup_type == BackupTypes.DAILY:
                current_daily_backups.append(f"{backup_name}.zip")
                for file in os.listdir(server.backup_dir):
                    if os.path.isfile(os.path.join(server.backup_dir, file)) and file not in current_daily_backups:
                        os.remove(os.path.join(server.backup_dir, file))

        self.bot.logger.info("Finished Routine Backups!")

    @_routine_backups.before_loop
    async def _before_routine(self):
        """
        This function runs before the daily backups loop starts.
        Ensures that the bot is ready before the loops start.
        """
        await self.bot.wait_until_ready()

    @mc_commands.command(name="backup")
    async def _server_backup(self, ctx: ServerCommandContext):
        """
        This is a server command. It lets you create a command directly from the Minecraft server using /backup.
        :param ctx: The context in which the command is being invoked
        :type ctx: ServerCommandContext
        """
        info = BACKUP_INFO.format(ctx.server.name, datetime.utcnow(), BackupTypes.MANUAL.value, author=self.bot.user)
        if not ctx.server.world_dir:
            await ctx.send(text=Text().add_component(
                text="Could not find the backup directory for this server", color=Colors.DARK_RED))
            return

        await ctx.send(text=Text().add_component(text="Creating a backup...", color="#9696FA"))
        backup_name = await asyncio.to_thread(lambda: _create_backup(ctx.server, BackupTypes.MANUAL, info))
        await ctx.send(text=Text().add_component(text=f"Backup {backup_name} created successfully", color="#32CD32"))
