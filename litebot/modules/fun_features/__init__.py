from . import memes

def setup(bot):
    bot.add_cog(memes.MemesCommand(bot))

def config(bot):
    return {
        "reddit": {
            "client_id": "",
            "client_secret": ""
        },
        "whitelisted_channels": []
    }