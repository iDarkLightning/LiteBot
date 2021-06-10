from .litebot import LiteBot


def main():
    bot_instance = LiteBot()
    bot_instance.start_server()

    bot_instance.plugin_manager.load_plugins()
    bot_instance.run(bot_instance.config["token"])

if __name__ == "__main__":
    main()