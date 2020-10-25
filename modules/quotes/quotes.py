import discord
from discord.ext import commands
from discord.utils import get
import sqlite3
import asyncio

bot = discord.Client()

class quotes(commands.Cog):
    
    def __init__(self, bot):
        self.client = bot
        self.conn = sqlite3.connect('./modules/quotes/quotes.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS quotes
                        (name text,
                        quote text)''')
    
    @commands.command()
    async def quotes(self, ctx, action=None, *, quote=None):
        if action == None:
            with self.conn:
                self.c.execute("SELECT * FROM quotes")
            quotes = self.c.fetchall()
            if quotes:
                if len(quotes) > 25:
                    embed_list = []
                    parts = [quotes[i:i + 15] for i in range(0, len(quotes), 15)]
                    for i in range(len(parts)):
                        embed = discord.Embed(title='Quotes')
                        for i in parts[i]:
                            embed.add_field(name=i[0], value=i[1], inline=False)
                        embed_list.append(embed)
                    pages = len(embed_list)
                    cur_page = 1
                    message = await ctx.send(embed=embed_list[cur_page-1])

                    await message.add_reaction("◀️")
                    await message.add_reaction("▶️")

                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
        
                    while True:
                        try:
                            reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)
                            if str(reaction.emoji) == "▶️" and cur_page != pages:
                                cur_page += 1
                                await message.edit(embed=embed_list[cur_page-1])
                                await message.remove_reaction(reaction, user)

                            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                                cur_page -= 1
                                await message.edit(embed=embed_list[cur_page-1])
                                await message.remove_reaction(reaction, user)

                            else:
                                await message.remove_reaction(reaction, user)
                        except asyncio.TimeoutError:
                            break
                else:
                    print(quotes)



        elif action.lower() == 'add':
            if quote != None:
                if 'https://discordapp.com/' not in quote:
                    with self.conn:
                        self.c.execute("INSERT INTO quotes VALUES (?, ?)", (ctx.author.name, quote))
                else:
                    quote = quote.split('/')
                    channel_id = int(quote[5])
                    message_id = int(quote[6])
                    print(channel_id, message_id)
                    channel = discord.utils.get(ctx.guild.text_channels, id=channel_id)
                    message = await channel.fetch_message(message_id)
                    with self.conn:
                        self.c.execute("INSERT INTO QUOTES VALUES (?, ?)", (message.author.name, message.content))


def setup(bot):
    bot.add_cog(quotes(bot))