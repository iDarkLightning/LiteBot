from aiohttp import web
from utils.utils import *

def get_members(request, client):
    try:
        role_ids = request.query["ids"].split(",")
        guild = client.get_guild(client.config["main_guild_id"])
        roles = [get(guild.roles, id=int(role_id)) for role_id in role_ids]
        members = [role.members for role in roles]
    except KeyError:
        return web.json_response({"error": "You did not provide the correct query param ids"})
    except AttributeError:
        return web.json_response({"error": "Invalid Guild ID or Role ID provided"})

    member_data = [
        {
            "name": member.name,
            "id": member.id,
            "discriminator": member.discriminator,
        } for member in [m for m in members][0]
    ]

    return web.json_response({"member_data": member_data})