import discord
from discord.ext import commands
import json
import requests
import re
import datetime
from datetime import datetime

bot = discord.Client()

with open('config.json') as json_file:
    config = json.load(json_file)


class Status(commands.Cog):

    def __init__(self, bot):
        self.client = bot

    @commands.command(brief="`status <server_name>` Displays server status")
    @commands.has_role(int(config["members_role"]))
    async def status(self, ctx, server_name):
        try:
            status = requests.get(
            f'https://api.mcsrvstat.us/2/{config["servers"][server_name.lower()]["server_ip"]}')
            json_data = status.json()
        except KeyError:
            await ctx.send(embed=discord.Embed(title=f'`{server_name}` is not a valid server', color=0xFF0000))
        else:
            online = json_data["online"]
            if online:
                embed = discord.Embed(
                    title=f'{ctx.message.guild} {server_name.upper()} Status', color=0x32CD32, timestamp=datetime.utcnow())
                online = 'Online'
                online_players = json_data["players"]["online"]
                max_players = json_data["players"]["max"]
                embed.add_field(name="Status", value=online)
                embed.add_field(name="Players Online",
                                value=f'{online_players}/{max_players}')
                if int(online_players) > 0:
                    players_online = re.sub(r'\s([?,!"](?:\s|$))', r'\1', str(json_data["players"]["list"]).translate(
                        {ord(c): " " for c in "!@#$%^&*()[]{};:'./<>?\|`~-=+"}).replace("_", "\_"))
                    embed.add_field(name="Online Players", value=(
                        players_online), inline=False)
                embed.set_thumbnail(url=f'{config["server_logo"]}')
                embed.set_footer(text=f'{ctx.message.guild}')
                await ctx.send(embed=embed)
            if not online:
                embed = discord.Embed(
                    title=f'{ctx.message.guild} {server_name.upper()} Status', color=0xFF0000, timestamp=datetime.utcnow())
                online = 'Offline'
                embed.add_field(name="Status", value=(online))
                embed.set_thumbnail(url=f'{config["server_logo"]}')
                embed.set_footer(text=f'{ctx.message.guild}')
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Status(bot))
