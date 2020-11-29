from modules.games import hangman

def setup(bot):
    bot.load_cog('games', hangman.HangmanGame(bot))

def config():
    return None