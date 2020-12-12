from LiteBot import LiteBot

bot = LiteBot()
bot.system_commands()
bot.error_handler()
print("Initalizing Modules...")
bot.init_modules()

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online!")

bot.run(bot.token)

