from discord.ext import flags
import json
from utils.utils import *


class ScoreBoard(commands.Cog):
    def __init__(self, client):
        self.client = client
        with open('./utils/scoreboards.json') as json_file:
            self.scoreboards = json.load(json_file)

    @flags.add_flag("--all", action="store_true")
    @flags.command(
        brief="`scoreboard <objective>` Displays the values for the objective similar to the sidebar in game. Use `--all` flag to include bots and unwhitelisted players",
        aliases=['sb'])
    async def scoreboard(self, ctx, objective_name, **flag):
        server_name = next(iter(self.client.servers))
        rcon = self.client.rcons[server_name]['rcon']

        if flag['all']:
            player_list = rcon.command('/scoreboard players list')
        else:
            player_list = rcon.command('/whitelist list')

        if objective_name in self.scoreboards:
            objective_name = self.scoreboards[objective_name]

        try:
            scores = {}
            for player in (player_list.replace(',', '')).split(' '):
                objective = rcon.command(f'/scoreboard players get {player} {objective_name}')

                if 'none' not in objective:
                    player_name = objective.split()[0]
                    objective_value = int(objective.split()[2])

                    scores.update({player_name: objective_value})
                    sort_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

            image = scoreboard_image(sort_scores, objective_name, scores_value=None)
            await ctx.send(file=image)

        except ValueError:
            await ctx.send(embed=discord.Embed(title=f"That scoreboard does not exist", color=0xFF0000))
        except UnboundLocalError:
            await ctx.send(embed=discord.Embed(title=f"That scoreboard shas no values", color=0xFF0000))
