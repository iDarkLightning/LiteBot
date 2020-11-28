import datetime
from datetime import datetime
import requests
from utils.utils import *


class Status(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief='`status <server_name> Displays server status')
    @perms_check('members_role')
    async def status(self, ctx, server_name=None):
        if server_name is None:
            server_name = get_server(self.client, ctx)
        status = requests.get(
            f'https://api.mcsrvstat.us/2/{self.client.servers[server_name.lower()]["server_ip"]}'
        )
        status_json = status.json()
        embed = discord.Embed(
            title=f'{ctx.message.guild} {server_name.upper()} Status', color=0x32CD32, timestamp=datetime.utcnow()
        )
        online = status_json['online']
        if online:
            online = 'Online'
            online_players = status_json['players']['online']
            max_players = status_json['players']['max']
            embed.add_field(name='Status', value=online)
            embed.add_field(name='Players Online', value=f'{online_players}/{max_players}')
            if online_players > 0:
                embed.add_field(name='Online Players', value=f'{", ".join(status_json["players"]["list"])}',
                                inline=False)
        else:
            online = 'Offline'
            embed.add_field(name="Status", value=online)
        embed.set_thumbnail(url=f'{self.client.config["server_logo"]}')
        embed.set_footer(text=f'{ctx.message.guild}')
        await ctx.send(embed=embed)
