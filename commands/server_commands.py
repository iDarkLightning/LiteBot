import discord
from discord.ext import commands
from discord.utils import get
import json
import utils
import bot as main

bot = discord.Client()
config = main.config

class server_commands(commands.Cog):
    
    def __init__(self, bot):
        self.client = bot
    
    def send_command(self, server_name, command):
        rcon = utils.rcon_connect(server_name, config)
        rcon.connect()
        resp = rcon.command(f'/{command}')
        return resp

    @commands.command(brief="`run <server_name> <command>` Can be used to run commands to the server")
    @commands.has_role(int(config["members_role"]))
    async def run(self, ctx, server_name, *, command):
        author = ctx.message.author
        operator_server = config["servers"][server_name.lower()]["operator"]
        if operator_server == 'True':
            role = discord.utils.get(author.guild.roles, id=(int(config["operator_role"])))
            if role in author.roles:
                resp = self.send_command(server_name, command)
                if resp:
                    await ctx.send(f"""```{resp}```""")
            else:
                 raise commands.CheckFailure
        elif operator_server == 'False':
            resp = self.send_command(server_name, command)
            if resp:
                await ctx.send(f"""```{resp}```""")

def setup(bot):
    bot.add_cog(server_commands(bot)) 