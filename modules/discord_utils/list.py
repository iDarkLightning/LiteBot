from utils.utils import *

class ListCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief="`list <role>` list all members with a role")
    async def list(self, ctx, role):
        if role == "@everyone":
            await ctx.send(embed=discord.Embed(title="Not currently supported", color=0xFF0000))
            return

        guild = self.client.get_guild(self.client.guild_id)

        roles = list(filter(lambda r: r.name == role, guild.roles))
        if len(roles) == 0:
            await ctx.send(embed=discord.Embed(title="That is not a valid role", color=0xFF0000))
            return

        members = [role.members for role in roles][0]

        embed = discord.Embed(
            title=f"There are {len(members)} members with role `{role}`",
            description="\n".join([member.name for member in members]),
            color=0xADD8E6
        )
        await ctx.send(embed=embed)