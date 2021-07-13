from __future__ import annotations
import os
import platform
import shutil
import zipfile
from datetime import datetime
from enum import Enum
from typing import Union, TYPE_CHECKING

BACKUP_INFO = "Server: {}\nMade By: {author} ({author.id})\nTime of Creation: {}\nType: {}"
TIME_FORMAT = '%m-%d-%y-%H-%M-%S'

if TYPE_CHECKING:
    from litebot.core.minecraft import MinecraftServer

class BackupTypes(Enum):
    MANUAL = "Manual"
    WEEKLY = "Weekly"
    DAILY = "Daily"

def create_backup(server: MinecraftServer, backup_type: BackupTypes, info: str) -> tuple[str, str]:
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
    backup_name = f"[{server.name.upper()}-{datetime.utcnow().strftime(TIME_FORMAT)}]"

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

    return backup_name, f"{os.path.join(backup_dir, backup_name)}.zip"

def restore_backup(server: MinecraftServer, backup_path: str) -> None:
    """
    Restores a backup for a server
    :param server: The server that you are restoring the backup for
    :type server: MinecraftServer
    :param backup_path: The path to the backup being restored
    :type backup_path: str
    """
    try:
        with zipfile.ZipFile(backup_path) as zf:
            zf.extractall(server.server_dir)

        os.rename(server.world_dir, os.path.join(server.server_dir, "world-BAK"))
        os.rename(os.path.join(server.server_dir, "backup"), server.world_dir)
        shutil.rmtree(os.path.join(server.server_dir, "world-BAK"))
    except Exception as e:
        os.rename(os.path.join(server.server_dir, "world-BAK"), server.world_dir)
        raise e

def creation_time(path: str) -> Union[float, int]:
    """
    Get's the creation time of a file from its path
    :param path: The path to the file
    :type path: str
    :return: The creation time
    :rtype: Union[float, int]
    """
    if platform.system() == "Windows":
        return os.path.getctime(path)
    else:
        stat = os.stat(path)
        try:
            return stat.st_birthtime
        except AttributeError:
            return stat.st_mtime

def convert_backup_path(backup_name: str, server: MinecraftServer) -> str:
    backup_path = None

    for root, dirs, files in os.walk(server.backup_dir):
        for file in files:
            if file == backup_name:
                backup_path = os.path.join(root, file)

    return backup_path