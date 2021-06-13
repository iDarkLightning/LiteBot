from .litebot import LiteBot
from .core.components import DiscordComponents

def main():
    bot_instance = LiteBot()
    DiscordComponents(bot_instance)
    bot_instance.start_server()

    bot_instance.plugin_manager.load_plugins()
    bot_instance.run(bot_instance.config["token"])

if __name__ == "__main__":
    main()