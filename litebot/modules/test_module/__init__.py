from .TestCog import TestCog

def setup(bot):
    bot.add_cog(TestCog(bot))

def config(bot):
    return {
        "test": "",
        "test1": ""
    }