import discord
from discord.ext import commands
from discord.utils import get
import json
import mcrcon
from mcrcon import MCRcon
import re
import time

bot = discord.Client()

with open ('config.json') as json_file:
    config = json.load(json_file) 

class tps(commands.Cog):
    
    def __init__(self, bot):
        self.client = bot
    
    @commands.command(brief="`tps <server_name>` Returns the server's TPS", aliases=['mspt'])
    @commands.has_role(int(config["members_role"]))
    async def tps(self, ctx, server_name):
        rcon = MCRcon(config["servers"][server_name.lower()]["server_ip_numerical"], config["servers"][server_name.lower()]["server_rcon_password"], config["servers"][server_name.lower()]["server_rcon_port"])
        rcon.connect()
        resp = rcon.command('/script run reduce(last_tick_times(),_a+_,0)/100;')
        mspt = (resp.split()[1])
        rcon.disconnect()
    
        if float(mspt) <= 50.0:
            tps = 20.0
        else:
            tps = 1000/float(mspt)
        
        mspt = (round(float(mspt), 1))
        tps = (round(float(tps), 1))
        if mspt <= 30:
            await ctx.send(embed= discord.Embed(title= f"TPS: {tps} MSPT: {mspt}", color=0x32CD32))
        elif mspt > 30 and mspt <= 50.0:
            await ctx.send(embed= discord.Embed(title= f"TPS: {tps} MSPT: {mspt}", color=0xFFA500))
        elif mspt > 50:
            await ctx.send(embed= discord.Embed(title= f"TPS: {tps} MSPT: {mspt}", color=0xFF0000))

def setup(bot):
    bot.add_cog(tps(bot)) 
