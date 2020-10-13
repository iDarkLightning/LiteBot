import discord
from discord.ext import commands, flags
from discord.utils import get
import json
import utils
import bot as main

bot = discord.Client()
config = main.config

with open ('scoreboards.json') as json_file:
    scoreboards = json.load(json_file) 

class scoreboard(commands.Cog):
    
    def __init__(self, bot):
        self.client = bot
    
    @flags.add_flag("--all", action="store_true")
    @flags.command(brief="`scoreboard <objective>` Displays the values for the objective similar to the sidebar in game. Use `--all` flag to include bots and unwhitelisted players", aliases=['sb'])
    async def scoreboard(self, ctx, objective_name, **flags):
        servers = config["servers"]
        server_name = next(iter(servers))
        rcon = utils.rcon_connect(server_name, config)

        def Convert(string):
                li = list(string.split(" "))
                return li
        
        rcon.connect()
        if flags['all'] == True:
            player_list = rcon.command(f'/scoreboard players list')
        else:
            player_list = rcon.command(f'/whitelist list')
        
        sami_datapack_check = rcon.command(f'/scoreboard players get {Convert(player_list)[1]} boman')
        if 'unknown' not in sami_datapack_check:
            using_sami_datapack = True
            print(using_sami_datapack)
        else:
            using_sami_datapack = False

        if using_sami_datapack == True:
            if str(objective_name) in scoreboards:
                objective_name = scoreboards[objective_name]
            else:
                objective_name = objective_name
        try:
            scores = {}

            for  word in Convert(player_list.replace(",", "")):
                objective = rcon.command(f'/scoreboard players get {word} {objective_name}')
                
                if "none" not in objective:
                    player_name = objective.split()[0]
                    objective_value = int(objective.split()[2])

                    scores.update({player_name: objective_value})
                    sort_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            image = utils.scoreboard_image(sort_scores, objective_name)
            await ctx.send(file= image)
            rcon.disconnect()

        except ValueError:
            await ctx.send(embed= discord.Embed(title=f"That scoreboard does not exist", color=0xFF0000))
        except UnboundLocalError:
            await ctx.send(embed= discord.Embed(title=f"That scoreboard shas no values", color=0xFF0000))
        

def setup(bot):
    bot.add_cog(scoreboard(bot)) 
