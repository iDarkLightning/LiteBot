import discord
from discord.ext import commands
import json
import datetime
from datetime import datetime
import shutil
import asyncio
from stat import S_ISREG, ST_CTIME, ST_MODE
import os
import sys
import time
import json
import bot as main

bot = discord.Client()
config = main.config

class backups(commands.Cog):

    def __init__(self, bot):
        self.client = bot

    @commands.command(brief="`backup <server_name> <create> or <list>`")
    @commands.has_role(int(config["operator_role"]))
    async def backup(self, ctx, server_name, action):
        if action == "create":
            author = ctx.author
            channel = ctx.channel
            timeout_embed = discord.Embed(title='Sorry your request has timed out', color=0xFF0000)
            name_query = await ctx.send(embed=discord.Embed(title='What would you like to name the backup?', description="Please do not use slashes"))

            def check(m):
                return m.channel == channel and m.author == author
            try:
                msg = await self.client.wait_for('message', check=check, timeout=60.0)
                backup_name = msg.content
                await msg.delete()
            except asyncio.TimeoutError:
                await name_query.edit(embed=timeout_embed)
                return
            else:
                embed = await ctx.send(embed=discord.Embed(title=f'Creating Backup `{backup_name}`', color=0xADD8E6))
                shutil.make_archive(f'{config["servers"][server_name]["backup_directory"]}/{backup_name}', 'zip', config["servers"][server_name]["world_directory"])
                embed.delete()
                await ctx.send(embed=discord.Embed(title=f'Backup `{backup_name}` created'))

        elif action == "list":
            dir_path = config["servers"][server_name]["backup_directory"]
            result = []

            data = (os.path.join(dir_path, fn) for fn in os.listdir(dir_path))
            data = ((os.stat(path), path) for path in data)

            data = ((stat[ST_CTIME], path)
                    for stat, path in data if S_ISREG(stat[ST_MODE]))

            for cdate, path in sorted(data):
                backups_list = (time.ctime(cdate), os.path.basename(path))
                result.append(backups_list*1)
                result_final = ("\n".join([" ".join(x) for x in result]))
            await ctx.send(f'```python\n{result_final}```')


def setup(bot):
    bot.add_cog(backups(bot))