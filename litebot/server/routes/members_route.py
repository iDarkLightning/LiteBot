import discord
from sanic import Blueprint, Request, json

blueprint = Blueprint("members", url_prefix="/members")

ROLES_QUERY = "/roles/<id:int>"
IN_GUILD_QUERY = "/<id:int>"

@blueprint.route(IN_GUILD_QUERY, methods=["GET"])
async def in_guild(request: Request, id: int):
    """
    Check if a member is in the main server guild
    :param id: The ID of the member
    :type id: int
    """
    guild = await request.app.config.BOT_INSTANCE.guild()
    member: discord.Member = await guild.fetch_member(id)

    if not member:
        return json({"error": "No member found!"})

    return json({"res": f"success! the user is in the guild {guild.name}"})

@blueprint.route(ROLES_QUERY, methods=["GET"])
async def fetch_roles(request: Request, id: int):
    """
    Fetch the roles for a member
    :param id: The ID of the member
    :type id: int
    """
    guild = await request.app.config.BOT_INSTANCE.guild()
    member: discord.Member = await guild.fetch_member(id)

    if not member:
        return json({"error": "No member found!"})

    return json({"res": [_serialize_role(role) for role in member.roles]})

def _serialize_role(role: discord.Role):
    return {
        "id": str(role.id),
        "name": role.name,
        "color": role.color.value
    }