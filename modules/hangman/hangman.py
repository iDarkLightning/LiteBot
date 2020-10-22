import random
import discord
from discord.ext import commands
from discord.utils import get
import json
import sqlite3
import re
import system.utils.utils as utils

bot = discord.Client()

class hangman(commands.Cog):
    
    def __init__(self, bot):
        self.client = bot
        self.conn = sqlite3.connect('./modules/hangman/hangman.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS players
                        (id integer, 
                        word text,
                        word_obscured text,
                        count integer,
                        guesses text,
                        message integer,
                        game_channel integer
                        )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS scores
                        (name text,
                        score integer
                        )''')
        self.c.execute("DELETE FROM players")
    
    def get_word(self):
        words = open('./modules/hangman/words.txt').read().splitlines()
        word = random.choice(words)
        return word.upper()
    
    @commands.command(brief='`hangman <play>|<guess>|<scores>` to play, guess, or view the leaderboard, ')
    async def hangman(self, ctx, action, guess=None):
        if action.lower() == 'play':
            self.c.execute("SELECT id FROM players WHERE id=?", (ctx.author.id,))
            result = self.c.fetchone()
            if not result:
                word = self.get_word()
                game_channel = ctx.message.channel.id
                word_obscured = ['_' for i in range(len(word))]
                message = await ctx.send(f'```ini\nThank you for playing hangman\n[{" ".join(word_obscured)}]\nYou have 7 tries```')
                with self.conn:
                    self.c.execute("INSERT INTO players VALUES (?, ?, ?, 7, ?, ?, ?)", (ctx.author.id, word, '|'.join(word_obscured), '|'.join([]), message.id, game_channel))
            else:
                await ctx.send(f'```diff\n-You are already in a game, please guess a valid letter or word with [hangman guess <guess>]```')
        elif action.lower() == 'guess':
            with self.conn:
                self.c.execute("SELECT * FROM players WHERE id=?", (ctx.author.id,))
            player_details = self.c.fetchone()
            if player_details == None:
                await ctx.send(f'```diff\n-You have not started a game, you can start one with [hangman play]```')
            elif guess == None:
                await ctx.send(f'```diff\n-Please guess a valid letter or word [hangman guess <guess>]```')
            else:
                await ctx.message.delete()
                game_channel = discord.utils.get(ctx.guild.text_channels, id=player_details[6])
                if ctx.message.channel.id != player_details[6]:
                    await ctx.send(f'```diff\n-Your current game is in``` {game_channel.mention}')
                else:
                    word = player_details[1]
                    word_obscured = player_details[2]
                    count_initial = player_details[3]
                    guess_list = player_details[4].split('|')
                    message = await game_channel.fetch_message(player_details[5])
                    await self.guess(ctx, word, word_obscured, guess.upper(), guess_list, count_initial, message)
        elif action.lower() == 'scores':
            await self.scores(ctx)

    async def guess(self, ctx, word, word_obscured, guess, guess_list, count_initial, message):
        def update_guess(guess, guess_list):
            with self.conn:
                guess_list.append(guess)
                self.c.execute("UPDATE players SET guesses=? WHERE id=?", ('|'.join(guess_list), ctx.author.id))
        word_list = list(''.join(word))            
        word_obscured = word_obscured.split('|')
        count = count_initial
        if guess.lower() not in word.lower() and guess.lower() in [i.lower() for i in guess_list]:
            await message.edit(content=f'```diff\n-You already guessed this, please try another guess```')
        elif len(guess) == 1 and guess.upper().isalpha():
            if guess in word_list:
                index = [i for i, x in enumerate(word_list) if x == guess]
                for i in index:
                    word_obscured[i] = guess.upper()
                    with self.conn:
                        self.c.execute("UPDATE players SET word_obscured=? WHERE id=?", ('|'.join(word_obscured), ctx.author.id))
                await message.edit(content=f"```ini\n[{' '.join(word_obscured)}]```")
                if '_' not in word_obscured:
                    await self.game_over(ctx, count, word, message, word_obscured, status='won')
            else:
                await self.game_over(ctx, count, word, message, word_obscured, status='wrong')
            update_guess(guess, guess_list)
        elif len(guess) == len(word):
            if guess.upper() == word:
                word_obscured = word_list
                await self.game_over(ctx, count, word, message, word_obscured, status='won')
            else:
                await self.game_over(ctx, count, word, message, word_obscured, status='wrong')
            update_guess(guess, guess_list)
        else:
            await message.edit(content=f"```diff\n-Invalid Guess! Please guess a valid letter or word\n-[{' '.join(word_obscured)}]```")
    
    async def game_over(self, ctx, count, word, message, word_obscured, status,):
        def clear_database():
            with self.conn:
                self.c.execute("DELETE FROM players WHERE id=?", (ctx.author.id,))
        if status == 'wrong':
            count -= 1
            with self.conn:
                self.c.execute("UPDATE players SET count=? WHERE id=?", (count, ctx.author.id))
            if count == 0:
                await message.edit(content=f'```diff\n-You lost the game, the word was {word}```')
                clear_database()
            else:
                await message.edit(content=f"```diff\n-Nope that was not correct, you have {count} tries left\n-[{' '.join(word_obscured)}]```")     
        elif status == 'won':
            await message.edit(content=f'```fix\n=You win, the word was indeed {word}```')
            clear_database()
            author = ctx.author.name
            self.c.execute("SELECT score FROM scores WHERE name=?", (author,))
            in_board = self.c.fetchone()
            if in_board:
                current_score = in_board[0]
                with self.conn:
                    self.c.execute("UPDATE scores SET score=? WHERE name=?", (current_score+1, author))
            else:
                with self.conn:
                    self.c.execute("INSERT INTO scores VALUES (?, '1')", (author,))
    
    async def scores(self, ctx):
        with self.conn:
            self.c.execute('SELECT name FROM scores')
        names = [''.join(i) for i in self.c.fetchall()]
        with self.conn:
            self.c.execute('SELECT score FROM scores')
        scores = [i[0] for i in self.c.fetchall()]
        scoreboard = dict(zip(names, scores))
        sort_scores = sorted(scoreboard.items(), key=lambda x: x[1], reverse=True)
        image = utils.scoreboard_image(sort_scores, 'Hangman Leaderboard', scores)
        await ctx.send(file=image)

def setup(bot):
    bot.add_cog(hangman(bot))