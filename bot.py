from LiteBot import LiteBot
from utils import console

bot = LiteBot()
bot.system_commands()
bot.error_handler()
console.log("Initalizing Modules...")
bot.init_modules()

@bot.event
async def on_ready():
    console.log(f"{bot.user.name} is online!")

bot.run(bot.token)

