from . import hangman

def setup(bot):
    bot.cog_loader.load(hangman.HangmanGame(bot))
