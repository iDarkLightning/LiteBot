from modules.quotes import quotes

def setup(bot):
    bot.add_cog(quotes.Quotes(bot))
