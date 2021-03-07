from .litebot import LiteBot

bot = LiteBot()

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online!")

bot.run(bot.config.token)
