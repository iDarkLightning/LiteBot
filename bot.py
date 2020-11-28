from LiteBot import LiteBot
import json
import platform

with open('config.json') as json_file:
    config = json.load(json_file)

print(platform.python_version())


bot = LiteBot()
bot.init_modules()
bot.system_commands()

@bot.event
async def on_ready():
    print(bot.user)



# bot.load_extension('main')
bot.run(bot.token)

