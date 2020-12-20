import asyncio
from random import randint
from utils.utils import *

class Quotes(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.cursor = self.client.db.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS quotes(
                            name TEXT,
                            messageID INTEGER,
                            quote TEXT)""")

    @commands.command(brief="`quote this|add|view <number> to add a quote or view quotes")
    async def quote(self, ctx, *args):
        if len(args) == 0 or args[0].isdigit():
            with self.client.db:
                self.cursor.execute("SELECT * FROM quotes")
            quotes = self.cursor.fetchall()

            if len(args) > 0 and int(args[0]) > len(quotes):
                await ctx.send(embed=discord.Embed(title=f"There are only {len(quotes)} quotes", color=0xFF0000))
                return

            if quotes:
                quote = quotes[randint(0, len(quotes)) if len(args) == 0 else int(args[0]) - 1]
                embed = discord.Embed(title="Quotes", color=0xADD8E6)
                embed.add_field(name=quote[0], value=quote[2])
                await ctx.send(embed=embed)

        elif args[0].lower() == "this":
            message_reference = ctx.message.reference
            message = await ctx.message.channel.fetch_message(message_reference.message_id)

            with self.client.db:
                self.cursor.execute("INSERT INTO quotes VALUES (?, ?, ?)", (message.author.name, message.id, message.content))

            await ctx.send(embed=discord.Embed(title="Quote added!", color=0xADD8E6))

        elif args[0].lower() == "view":
            with self.client.db:
                self.cursor.execute("SELECT * FROM quotes")
            quotes = self.cursor.fetchall()

            if quotes:
                if len(quotes) > 25:
                    embed_list = []
                    parts = [quotes[i:i + 15] for i in range(0, len(quotes), 15)]
                    count = 1
                    for i in range(len(parts)):
                        embed = discord.Embed(title='Quotes', color=0xADD8E6)
                        for i in parts[i]:
                            embed.add_field(name=f"{i[0]} #{count}", value=i[2], inline=False)
                            count += 1
                        embed_list.append(embed)
                    pages = len(embed_list)
                    cur_page = 1
                    message = await ctx.send(embed=embed_list[cur_page - 1])

                    await message.add_reaction("◀️")
                    await message.add_reaction("▶️")

                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

                    while True:
                        try:
                            reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)
                            if str(reaction.emoji) == "▶️" and cur_page != pages:
                                cur_page += 1
                                await message.edit(embed=embed_list[cur_page - 1])
                                await message.remove_reaction(reaction, user)

                            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                                cur_page -= 1
                                await message.edit(embed=embed_list[cur_page - 1])
                                await message.remove_reaction(reaction, user)

                            else:
                                await message.remove_reaction(reaction, user)
                        except asyncio.TimeoutError:
                            break
                else:
                    embed = discord.Embed(title="Quotes", color=0xADD8E6)
                    count = 1
                    for quote in quotes:
                        embed.add_field(name=f"{quote[0]} #{count}", value=quote[2], inline=False)
                        count += 1

                    await ctx.send(embed=embed)
            else:
                await ctx.send(embed=discord.Embed(title="There are no quotes",color=0xFF0000))

        elif args[0] == "add":
            member = ctx.message.mentions[0].name
            quote = " ".join(args[2:])

            with self.client.db:
                self.cursor.execute("INSERT INTO quotes VALUES (?,?,?)", (member,0,quote))

            await ctx.send(embed=discord.Embed(title="Quote Added!", color=0xADD8E6))


