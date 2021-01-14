from aiohttp import web
from utils.utils import *

def get_members(request, client):
    guild = client.get_guild(client.config["main_guild_id"])
    members_role = get(guild.roles, id=client.config["members_role"][0])
    members = members_role.members

    member_data = [
        {
            "name": member.name,
            "id": member.id,
            "discriminator": member.discriminator,
        } for member in members
    ]

    return web.json_response({"member_data": member_data})