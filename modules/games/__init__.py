from modules.games import hangman

def setup(bot):
    bot.add_cog(hangman.HangmanGame(bot))
