import os
from litebot.minecraft.server import MinecraftServer


def convert_backup_path(backup_name: str, server: MinecraftServer) -> str:
    backup_path = None

    for root, dirs, files in os.walk(server.backup_dir):
        for file in files:
            if file == backup_name:
                backup_path = os.path.join(root, file)

    return backup_path