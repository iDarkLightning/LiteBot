from .litebot import LiteBot

bot = LiteBot()

@bot.event
async def on_ready():
    bot.logger.info(f"{bot.user.name} is online!")

bot.run(bot.config.token)
