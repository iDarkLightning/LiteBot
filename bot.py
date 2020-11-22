from LiteBot import LiteBot
import json

with open('config.json') as json_file:
    config = json.load(json_file)

bot = LiteBot()
#bot.load_extension('main')
bot.run(bot.token)