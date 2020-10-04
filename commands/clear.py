import discord
from discord.utils import get
from discord.ext import commands
import json

bot = discord.Client()


with open('config.json') as json_file:
    config = json.load(json_file)


class discord_management(commands.Cog):

    @commands.command(brief="`clear <number>` deletes the last <number> messages sent in the channel")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, message_count=5):
        await ctx.channel.purge(limit=message_count+1)


def setup(bot):
    bot.add_cog(discord_management(bot))
