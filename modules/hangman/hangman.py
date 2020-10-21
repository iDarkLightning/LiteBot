import random
from random_word import RandomWords
import discord
from discord.ext import commands
import json
import sqlite3
import re
import system.utils.utils as utils

bot = discord.Client()
r = RandomWords()

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
                        guesses text
                        )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS scores
                        (name text,
                        score text
                        )''')
        self.c.execute("DELETE FROM players")
    
    def get_word(self):
        words = open('./modules/hangman/words.txt').read().splitlines()
        word = random.choice(words)
        return word.upper()
    
    @commands.command()
    async def hangman(self, ctx, action, guess=None):
        if action.lower() == 'play':
            self.c.execute("SELECT id FROM players WHERE id=?", (ctx.author.id,))
            result = self.c.fetchone()
            if not result:
                word = self.get_word()
                print(word)
                word_obscured = ['_' for i in range(len(word))]
                with self.conn:
                    self.c.execute("INSERT INTO players VALUES (?, ?, ?, 7, ?)", (ctx.author.id, word, '|'.join(word_obscured), '|'.join([])))
                await ctx.send(f'```{" ".join(word_obscured)}```')
            else:
                await ctx.send(embed=discord.Embed(title='You are already in a game, please do `hangman guess` to play', color=0xFF0000))
        elif action.lower() == 'guess':
            with self.conn:
                self.c.execute("SELECT * FROM players WHERE id=?", (ctx.author.id,))
            player_details = self.c.fetchone()
            if player_details == None:
                await ctx.send(embed=discord.Embed(title='You have not started a game, please do `hangman play` to play', color=0xFF0000))
            elif guess == None:
                await ctx.send(embed=discord.Embed(title='Please guess a valid letter or word `hangman guess <guess>`', color=0xFF0000))
            else:
                word = player_details[1]
                word_list = list(''.join(word))
                word_obscured = player_details[2]
                count_initial = player_details[3]
                guess_list = player_details[4].split('|')
                await self.guess(ctx, word, word_obscured, word_list, guess.upper(), guess_list, count_initial)
        elif action.lower() == 'scores':
            await self.scores(ctx)

    async def guess(self, ctx, word, word_obscured, word_list, guess, guess_list, count_initial):
        def update_guess(guess, guess_list):
            with self.conn:
                guess_list.append(guess)
                self.c.execute("UPDATE players SET guesses=? WHERE id=?", ('|'.join(guess_list), ctx.author.id))            
        word_obscured = word_obscured.split('|')
        count = count_initial
        if guess.lower() not in word.lower() and guess.lower() in [i.lower() for i in guess_list]:
            await ctx.send(embed=discord.Embed(title='You already guessed this', color=0xFF0000))
        elif len(guess) == 1 and guess.upper().isalpha():
            if guess in word_list:
                index = [i for i, x in enumerate(word_list) if x == guess]
                for i in index:
                    word_obscured[i] = guess.upper()
                    with self.conn:
                        self.c.execute("UPDATE players SET word_obscured=? WHERE id=?", ('|'.join(word_obscured), ctx.author.id))
                await ctx.send(f"```{' '.join(word_obscured)}```")
                if '_' not in word_obscured:
                    await self.game_over(ctx, count, word, status='won')
            else:
                await self.game_over(ctx, count, word, status='wrong')
            update_guess(guess, guess_list)
        elif len(guess) == len(word):
            if guess.upper() == word:
                word_obscured = word_list
                await self.game_over(ctx, count, word, status='won')
            else:
                await self.game_over(ctx, count, word, status='wrong')
            update_guess(guess, guess_list)
        else:
            await ctx.send(embed=discord.Embed(title='Invalid guess, please guess a valid letter or word', color=0xFF0000))
    
    async def game_over(self, ctx, count, word, status):
        def clear_database():
            with self.conn:
                self.c.execute("DELETE FROM players WHERE id=?", (ctx.author.id,))

        if status == 'wrong':
            count -= 1
            with self.conn:
                self.c.execute("UPDATE players SET count=? WHERE id=?", (count, ctx.author.id))
            if count == 0:
                await ctx.send(embed=discord.Embed(
                    title=f'You lost the game, the word was `{word}`',
                    color=0xFF0000))
                clear_database()
            else:
                await ctx.send(embed=discord.Embed(
                    title=f'Nope, that was not correct, you have {count} tries left',
                    color=0xFF0000))     
        elif status == 'won':
            await ctx.send(embed=discord.Embed(
                title=f'You Win, The word was indeed {word}',
                color=0xADD8E6))
            clear_database()
            author = str(ctx.author).partition('#')
            self.c.execute("SELECT score FROM scores WHERE name=?", (author[0],))
            in_board = self.c.fetchone()
            if in_board:
                current_score = in_board[0]
                print(type(current_score))
                print(current_score)
                with self.conn:
                    self.c.execute("UPDATE scores SET score=? WHERE name=?", (current_score+1, author[0]))
            else:
                with self.conn:
                    self.c.execute("INSERT INTO scores VALUES (?, '1')", (author[0],))
    
    async def scores(self, ctx):
        with self.conn:
            self.c.execute('SELECT name FROM scores')
        names = self.c.fetchall()
        names = [''.join(i) for i in names]
        with self.conn:
            self.c.execute('SELECT score FROM scores')
        scores = self.c.fetchall()
        scores = [i[0] for i in scores]
        scoreboard = dict(zip(names, scores))
        sort_scores = sorted(scoreboard.items(), key=lambda x: x[1], reverse=True)
        image = utils.scoreboard_image(sort_scores, 'Hangman Leaderboard', scores)
        await ctx.send(file=image)

def setup(bot):
    bot.add_cog(hangman(bot))