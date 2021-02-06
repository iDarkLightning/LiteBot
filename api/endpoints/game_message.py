from aiohttp import web
from utils.utils import *

async def send_game_message(request, client):
    data = await request.json()
    server = client.servers[data["server_name"]]
    guild = client.get_guild(client.guild_id)
    bridge_channel = get(guild.text_channels, id=server["bridge_channel_id"])
    await bridge_channel.send(data["message"])

    return web.json_response({"message": "Success"})