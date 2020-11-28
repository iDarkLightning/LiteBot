from utils.utils import *


class Tps(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief="`tps <server_name>` Returns the server's TPS", aliases=['mspt'])
    @perms_check('members_role')
    async def tps(self, ctx, server_name=None):
        if server_name is None:
            server_name = get_server(self.client, ctx)

        rcon = self.client.rcons[server_name.lower()]['rcon']
        response = rcon.command('/script run reduce(last_tick_times(),_a+_,0)/100;')
        mspt = round(float(response.split()[1]), 1)

        if mspt <= 50.0:
            tps = 20.0
        else:
            tps = 1000 / mspt

        tps = round(float(tps), 1)
        if mspt <= 30:
            await ctx.send(embed=discord.Embed(title=f"TPS: {tps} MSPT: {mspt}", color=0x32CD32))
        elif 30 < mspt <= 50.0:
            await ctx.send(embed=discord.Embed(title=f"TPS: {tps} MSPT: {mspt}", color=0xFFA500))
        elif mspt > 50:
            await ctx.send(embed=discord.Embed(title=f"TPS: {tps} MSPT: {mspt}", color=0xFF0000))
