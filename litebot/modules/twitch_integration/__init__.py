from . import chat

def setup(bot):
    bot.add_cog(chat.TwitchChat(bot))

def config(bot):
    return {
        "token": "",
        "nick": "THIS NEEDS TO BE YOUR ACCOUNT NAME",
        "client_id": ""
    }