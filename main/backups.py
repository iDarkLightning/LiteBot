import asyncio
import datetime
from datetime import datetime
import zipfile
from pathlib import Path
import os
from utils.utils import *


class Backups(commands.Cog):
    def __init__(self, client):
        self.client = client
        for server in self.client.servers:
            Path(f'{self.client.servers[server]["backup_directory"]}\\manual').mkdir(exist_ok=True)
            Path(f'{self.client.servers[server]["backup_directory"]}\\weekly').mkdir(exist_ok=True)

    @commands.Cog.listener()
    async def on_ready(self):
        self.routine_backups.start()

    @commands.command(brief="`backup <server_name>` Creates a backup of the server's world")
    @perms_check('operator_role')
    async def backup(self, ctx, server_name=None):
        if server_name is None:
            server_name = get_server(self.client, ctx)

        info = f'Server: {ctx.guild}-{server_name}\nMade By: {ctx.author} ({ctx.author.id})\nTime of Creation: {datetime.utcnow()}\nType: Manual'

        await ctx.send(embed=discord.Embed(title='Creating a backup...'))
        backup_name = await asyncio.to_thread(lambda: self.create_backup(server_name, 'manual', info))
        await ctx.send(embed=discord.Embed(title=f'Backup {backup_name} Created'))

    @tasks.loop(hours=24.0)
    async def routine_backups(self):
        current_daily_backups = []
        for server in self.client.servers:
            info = f'Server: {server}\nMade By: {self.client.user} ({self.client.user.id})\nTime of Creation: {datetime.utcnow()}'
            if datetime.today().weekday() == 6:
                info = info + '\nType: Weekly'
                await asyncio.to_thread(lambda: self.create_backup(server, 'weekly', info))
            else:
                info = info + '\nType: Daily'
                backup_name = await asyncio.to_thread(lambda: self.create_backup(server, 'daily', info))
                current_daily_backups.append(f'{backup_name}.zip')
                backups_path = self.client.servers[server]['backup_directory']
                for file in os.listdir(backups_path):
                    if os.path.isfile(os.path.join(backups_path, file)) and file not in current_daily_backups:
                        os.remove(os.path.join(self.client.servers[server]['backup_directory'], file))

    def create_backup(self, server, backup_type, info):
        backup_name = f'[{server.upper()}] {datetime.utcnow().strftime("%m-%d-%y %H-%M-%S")}'
        world_dir = self.client.servers[server]['world_directory']

        if backup_type != 'daily':
            backup_dir = f'{self.client.servers[server]["backup_directory"]}\\{backup_type}'
        else:
            backup_dir = f'{self.client.servers[server]["backup_directory"]}'

        with zipfile.ZipFile(f'{backup_dir}\\{backup_name}.zip', 'w', compression=zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(world_dir):
                for file in files:
                    path = os.path.join(root, file)
                    zip_file.write(path, f'backup\\{os.path.relpath(path, start=world_dir)}')
            zip_file.writestr('info.txt', info)

        return backup_name
