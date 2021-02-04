import random
from utils.utils import *


class Hangman():
    instances = []

    def __init__(self, client, player, message, channel):
        Hangman.instances.append(self)
        self.client = client
        self.player = player
        self.message = message
        self.channel = channel
        self.word = self.get_word()
        self.word_list = list(''.join(self.word))
        self.word_obscured = ['_' for i in range(len(self.word))]
        self.attempts = 7
        self.guesses = []
        self.cursor = self.client.db.cursor()

    def get_word(self):
        words = open('./modules/games/hangman_words.txt').read().splitlines()
        word = random.choice(words)
        return word.upper()

    async def guess(self, guess: str):
        if guess.upper() in self.guesses:
            await self.message.edit(content=f"```diff\n-You already guessed this, please try another guess\n[{' '.join(self.word_obscured)}]```")
        elif len(guess) == 1 and guess.upper().isalpha():
            self.guesses.append(guess)
            if guess.upper() in self.word_list:
                index = [i for i, x in enumerate(self.word_list) if x == guess]
                for i in index:
                    print(index)
                    self.word_obscured[i] = guess.upper()
                await self.message.edit(content=f"```ini\n[{' '.join(self.word_obscured)}]```")
                if '_' not in self.word_obscured:
                    await self.game_over('won')
            else:
                await self.game_over('wrong')
        elif len(guess) == len(self.word):
            self.guesses.append(guess)
            if guess.upper() == self.word:
                self.word_obscured = self.word_list
                await self.game_over('won')
            else:
                await self.game_over('wrong')
        else:
            await self.message.edit(content=f"```diff\n-Invalid Guess! Please guess a valid letter or word\n-[{' '.join(self.word_obscured)}]```")

    async def game_over(self, status: str):
        if status == 'wrong':
            self.attempts -= 1
            if self.attempts == 0:
                await self.message.edit(content=f"```diff\n-You lost the game, the word was {self.word}```")
                Hangman.instances.remove(self)
            else:
                await self.message.edit(content=f"```diff\n-Nope that was not correct, you have {self.attempts} tries left\n-[{' '.join(self.word_obscured)}]```")
        elif status == 'won':
            await self.message.edit(content=f"```fix\n=You win! The word was indeed {self.word}```")
            Hangman.instances.remove(self)
            self.update_score()

    def update_score(self):
        with self.client.db:
            self.cursor.execute('SELECT score FROM hangman_scores WHERE name=?', (self.player.name,))
        in_board = self.cursor.fetchone()
        if in_board:
            current_score = in_board[0]
            with self.client.db:
                self.cursor.execute('UPDATE hangman_scores SET score=? WHERE name=?', (current_score+1, self.player.name))
        else:
            with self.client.db:
                self.cursor.execute('INSERT INTO hangman_scores VALUES (?, 1)', (self.player.name,))

class HangmanGame(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.cursor = self.client.db.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS hangman_scores (
                            name text,
                            score integer)""")

    @commands.command(brief='`hangman <play>|<guess>|<scores>` to play, guess, or view the leaderboard')
    async def hangman(self, ctx, action, guess=None):
        if action.lower() == 'play':
            in_game = list(filter(lambda x: x.player == ctx.author, Hangman.instances))
            if len(in_game) == 0:
                message = await ctx.send(f"```ini\nThank you for playing hangman```")
                game = Hangman(self.client, ctx.author, message, ctx.message.channel)
                print(game.word)
                await message.edit(content=f"```ini\nThank you for playing hangman\n[{' '.join(game.word_obscured)}]\nYou have 7 tries```")
            else:
                await ctx.send(f"```diff\nYou are already in a game. Please guess a valid letter or word with [hangman guess <guess>]``` {in_game[0].channel.mention}")
        elif action.lower() == 'guess':
            in_game = list(filter(lambda x: x.player == ctx.author, Hangman.instances))
            if len(in_game) == 0:
                await ctx.send(f'```diff\n-You have not started a game, you can start one with [hangman play]```')
            elif guess is None:
                await ctx.send(f'```diff\n-Please guess a valid letter or word [hangman guess <guess>]```')
            else:
                game = in_game[0]
                await ctx.message.delete()
                if ctx.message.channel != game.channel:
                    await ctx.send(f'```diff\n-Your current game is in``` {game.channel.mention}')
                else:
                    await game.guess(guess.upper())
        elif action == 'scores':
            with self.client.db:
                self.cursor.execute('SELECT name FROM hangman_scores')
            names = [''.join(i) for i in self.cursor.fetchall()]
            with self.client.db:
               self.cursor.execute('SELECT score FROM hangman_scores')
            scores = [i[0] for i in self.cursor.fetchall()]
            scoreboard = dict(zip(names, scores))
            sort_scores = sorted(scoreboard.items(), key=lambda x: x[1], reverse=True)
            image = scoreboard_image(sort_scores, 'Hangman', scores)
            await ctx.send(file=image)
