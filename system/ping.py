import discord
from discord.utils import get
from discord.ext import commands
import time
import datetime
from datetime import datetime
import bot as main

bot = discord.Client()

class ping(commands.Cog):
    
    def __init__(self, bot):
        self.client = bot
    
    @commands.command(brief="`.ping` or `.pong` Returns the bot's latency to discord", aliases=['ping', 'pong'])
    async def latency(self, ctx):
        before = time.time()

        message = await ctx.send(embed=discord.Embed(
            title='Checking Latency',
            colour=discord.Colour.blue(),
            timestamp=datetime.now())
            .set_footer(text='{0.display_name}#{0.discriminator}'.format(ctx.author), icon_url=ctx.author.avatar_url))

        after = time.time()
        latency = after - before

        await message.edit(embed=discord.Embed(
            title='Latency',
            colour=(0xADD8E6),
            timestamp=datetime.now())
            .add_field(name='WebSocket Latency', value='{0:.2f}ms'.format(self.client.latency * 1000))
            .add_field(name='HTTP Latency', value='{0:.2f}ms'.format(latency * 1000))
            .set_footer(text='{0.display_name}#{0.discriminator}'.format(ctx.author), icon_url=ctx.author.avatar_url))

def setup(bot):
    bot.add_cog(ping(bot))